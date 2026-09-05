from flask import Flask, render_template
from sqlalchemy import create_engine, text, URL, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import SQLAlchemyError



import os

app = Flask(__name__)

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

class Base(DeclarativeBase):
    pass

class item(Base):
    __tablename__ = "item_info"

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False)


    def __repr__(self):
        return f""



engine = create_engine(url, echo=True, pool_pre_ping=True)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)