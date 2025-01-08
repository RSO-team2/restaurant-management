import os
import psycopg2
import bcrypt
from dotenv import load_dotenv
from flask import Flask, request, jsonify


ADD_RESTAURANT="INSERT INTO restaurants (name, type) VALUES (%s,%s) RETURNING id"
ADD_MENU_ITEM="INSERT INTO menu_items (name, price) VALUES (%s, %s) RETURNING id"
ADD_MENU="INSERT INTO menus (restaurant_id, items) VALUES (%s, %s) RETURNING id"
load_dotenv()

app = Flask(__name__)

@app.post("/add_restaurant")
def add_restaurant():
    data = request.get_json()
    res_name = data["name"]
    res_type = data["type"]

    connection = psycopg2.connect("DATABASE_URL")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(ADD_RESTAURANT, (res_name, res_type,))
            res_id = cursor.fetchone()[0]

    return jsonify({"restaurant_id": res_id})


@app.post("/add_menu_item")
def add_menu_item():
    data = request.get_json()
    name = data["name"]
    price = data["price"]

    connection = psycopg2.connect("DATABASE_URL")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(ADD_MENU_ITEM, (name, price,))
            menu_item_id = cursor.fetchone()[0]

    return jsonify({"menu_item_id": menu_item_id})

@app.post("/add_menu")
def add_menu():
    data = request.get_json()
    restaurant_id = data["restaurant_id"]
    items = data["items"]

    connection = psycopg2.connect("DATABASE_URL")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(ADD_MENU, (restaurant_id, items,))
            menu_id = cursor.fetchone()[0]

    return jsonify({"menu_id": menu_id})

if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5001)