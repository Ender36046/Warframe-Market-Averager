from sqlalchemy import create_engine, text, URL, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import SQLAlchemyError
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
    historical_med: Mapped[float] =  mapped_column()
    recent_med : Mapped[float] = mapped_column()
    recent_wa : Mapped[float] = mapped_column()
    sr_med : Mapped[float] = mapped_column()

    def __repr__(self) -> str:
        return f""


def main():
    #Base.metadata.create_all(engine)
    pass

if __name__ == "__main__":
    main()