from sqlalchemy import create_engine, text, URL, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import SQLAlchemyError

from stats import median_prices, get_all_items
import os

USERNAME = os.getenv("USERNAME") 
PASSWORD = os.getenv("PASSWORD") 
HOST = os.getenv("HOST") 
PORT = os.getenv("PORT") 
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

        ranks = [entry.max_rank, 0] if entry.max_rank else [None]

        for rank in ranks:
            stats = median_prices(entry.slug, mod_rank= rank)
            if(stats["historical_med"] == None and stats["recent_med"] == None and stats["recent_wa"]  == None and stats["sr_med"] == None):
                continue
            else: 
                tradable = True
                stat = Stat(
                    id = entry.id,
                    item_rank = rank,
                    historical_med = stats["historical_med"],
                    recent_med = stats["recent_med"],
                    recent_wa = stats["recent_wa"],
                    sr_med = stats["sr_med"]
                )
                entry.stats.append(stat)

        if(tradable):
            session.add(entry)
            session.commit()


def main():
    Base.metadata.drop_all(engine)
    """Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session)"""
    

if __name__ == "__main__":
    main()