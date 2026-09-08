from sqlalchemy import create_engine, text, URL, inspect, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
import datetime, zoneinfo

from stats import median_prices, get_all_items, get_item_stats, get_current_prices
import os

USERNAME = os.getenv("DB_USERNAME") 
PASSWORD = os.getenv("DB_PASSWORD") 
HOST = os.getenv("DB_HOST") 
PORT = os.getenv("DB_PORT") 
PORT_INT = int(PORT) if PORT is not None else None 
DATABASE = os.getenv("DATABASE")


url = URL.create(
    drivername= "postgresql+psycopg",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT_INT,
    database=DATABASE
)

engine = create_engine(url, echo=True, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "item_info"

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    max_rank : Mapped[int] = mapped_column(nullable=True)
    stats : Mapped[list["Stat"]] = relationship()

    def __repr__(self) -> str:
        return f""

class Stat(Base):
    __tablename__ = "statistics"

    id: Mapped[str] = mapped_column(ForeignKey("item_info.id"), primary_key=True)
    item_rank: Mapped[int] = mapped_column(primary_key=True, default=-1)
    historical_med: Mapped[float] =  mapped_column(nullable=True)
    recent_med : Mapped[float] = mapped_column(nullable=True)
    recent_wa : Mapped[float] = mapped_column(nullable=True)
    sr_med : Mapped[float] = mapped_column(nullable=True)
    num_sell : Mapped[int] = mapped_column(nullable= True)
    num_buy : Mapped[int] = mapped_column(nullable= True)
    last_update : Mapped[str] = mapped_column(nullable= False)

    def __repr__(self) -> str:
        return f""

def seed(session: Session):
    items = get_all_items()
    
    for item in items:
        tradable = False
        entry = Item(
            id = item["id"],
            slug = item["slug"],
            name = item["i18n"]["en"]["name"],
            max_rank = item.get("maxRank"),
        )

        ranks = [entry.max_rank, 0] if entry.max_rank is not None else [-1]

        for rank in ranks:
            stats = get_item_stats(entry.slug)
            median_stats = median_prices(stats, mod_rank= rank)
            current_stats = get_current_prices(entry.slug, mod_rank=rank)
            current_buy = current_stats["buy"]
            current_sell = current_stats["sell"]

            good_buys = 0
            good_sells = 0

            comparison_value = None
            values = [median_stats["recent_wa"],median_stats["sr_med"], median_stats["recent_med"], median_stats["historical_med"]]
            comparison_value = next((x for x in values if x is not None), None)

            if(median_stats["historical_med"] == None and median_stats["recent_med"] == None and median_stats["recent_wa"]  == None and median_stats["sr_med"] == None):
                session.add(entry)
                session.commit()
            else: 
                if(current_buy!=None and comparison_value != None):
                    for price in current_buy:
                        if(price > comparison_value * 0.90):
                            good_buys += current_buy[price]

                if(current_sell!=None and comparison_value !=None):
                    for price in current_sell:
                        if(price < comparison_value * 0.10):
                            good_sells += current_sell[price]

                tradable = True
                time = datetime.datetime.now(zoneinfo.ZoneInfo("EST"))

                stat = Stat(
                    id = entry.id,
                    item_rank = rank,
                    historical_med = median_stats["historical_med"],
                    recent_med = median_stats["recent_med"],
                    recent_wa = median_stats["recent_wa"],
                    sr_med = median_stats["sr_med"],
                    num_sell = good_sells,
                    num_buy = good_buys,
                    last_update = time.strftime("%d-%m-%Y %H:%M:%S EST")
                )
                entry.stats.append(stat)

        if(tradable):
            session.add(entry)
            session.commit()

def upsert_stats(session: Session, id: str, item_rank, historical_med, recent_med, recent_wa, sr_med, num_sell, num_buy, last_update):
    statement = insert(Stat).values(
        id = id,
        item_rank = item_rank,
        historical_med = historical_med,
        recent_med = recent_med,
        recent_wa = recent_wa,
        sr_med = sr_med,
        num_sell = num_sell,
        num_buy = num_buy,
        last_update = last_update
    )

    statement = statement.on_conflict_do_update(
        index_elements=["id","item_rank"],
        set_=dict(
            historical_med = historical_med,
            recent_med = recent_med,
            recent_wa = recent_wa,
            sr_med = sr_med,
            num_sell = num_sell,
            num_buy = num_buy,
            last_update = last_update
        )
    )

    session.execute(statement)
    session.commit()

def upsert_all(session :Session):
    items = get_all_items()
    for item in items:
        tradable = False
        max_rank = item.get("maxRank")
        ranks = [max_rank, 0] if max_rank is not None else [-1]
        slug = item["slug"]
        time = datetime.datetime.now(zoneinfo.ZoneInfo("EST"))

        for rank in ranks:
            stats = get_item_stats(slug)
            median_stats = median_prices(stats, mod_rank= rank)
            current_stats = get_current_prices(slug, mod_rank=rank)
            current_buy = current_stats["buy"]
            current_sell = current_stats["sell"]

            good_buys = 0
            good_sells = 0

            comparison_value = None
            values = [median_stats["recent_wa"],median_stats["sr_med"], median_stats["recent_med"], median_stats["historical_med"]]
            comparison_value = next((x for x in values if x is not None), None)

            if(median_stats["historical_med"] == None and median_stats["recent_med"] == None and median_stats["recent_wa"]  == None and median_stats["sr_med"] == None):
                continue
            else: 
                if(current_buy!=None and comparison_value != None):
                    for price in current_buy:
                        if(price > comparison_value * 0.90):
                            good_buys += current_buy[price]

                if(current_sell!=None and comparison_value !=None):
                    for price in current_sell:
                        if(price < comparison_value * 0.10):
                            good_sells += current_sell[price]

                tradable = True
                

            if(tradable):
                upsert_stats(session, item["id"], rank, median_stats["historical_med"], median_stats["recent_med"],median_stats["recent_wa"],median_stats["sr_med"], good_sells, good_buys, time.strftime("%d-%m-%Y %H:%M:%S EST"))

def main():
    inspector = inspect(engine)
    with Session(engine) as session:
        if(not inspector.has_table("item_info")):
            Base.metadata.create_all(engine)
            seed(session)
        else:
            print("Already seeded")
        upsert_all(session)

if __name__ == "__main__":
    main()