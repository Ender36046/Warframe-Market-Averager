import sys

sys.dont_write_bytecode = True

from flask import Flask, render_template, jsonify, abort, request
from sqlalchemy.orm import Session
from sqlalchemy import select
from db import engine, Item, Stat

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/items/<item_slug>")
def item(item_slug):
    with Session(engine) as session:
        stmt = select(Item).where(Item.slug == item_slug)
        item = session.execute(stmt).scalars().first()
        #print("THIS IS THE ITEM", item)
        print("HI")
        if item == None:
            abort(404)
        return render_template("item.html",item = item, item_name = item.name, stats = item.stats)
        


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug= True)