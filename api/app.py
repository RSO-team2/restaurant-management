import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

ADD_RESTAURANT = "INSERT INTO restaurants (name, type, rating, address, average_time, price_range) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id"
ADD_MENU_ITEM = "INSERT INTO menu_items (name, price) VALUES (%s, %s) RETURNING id"
ADD_MENU = "INSERT INTO menus (restaurant_id, items) VALUES (%s, %s) RETURNING id"
load_dotenv()

app = Flask(__name__)
cors = CORS(app)


@app.post("/add_restaurant")
@cross_origin()
def add_restaurant():
    data = request.get_json()
    res_name = data["name"]
    res_type = data["type"]
    res_rating = data["rating"]
    res_address = data["address"]
    res_avg_time = data["average_time"]
    res_price_range = data["price_range"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                ADD_RESTAURANT,
                (
                    res_name,
                    res_type,
                    res_rating,
                    res_address,
                    res_avg_time,
                    res_price_range,
                ),
            )
            res_id = cursor.fetchone()[0]

    return jsonify({"restaurant_id": res_id})


@app.get("/get_restaurants")
@cross_origin()
def get_restaurants():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM restaurants")
            restaurants = cursor.fetchall()

    return jsonify({"resturant_list": restaurants})


@app.post("/add_menu_item")
@cross_origin()
def add_menu_item():
    data = request.get_json()
    name = data["name"]
    price = data["price"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                ADD_MENU_ITEM,
                (
                    name,
                    price,
                ),
            )
            menu_item_id = cursor.fetchone()[0]

    return jsonify({"menu_item_id": menu_item_id})


@app.get("/get_menu_items")
@cross_origin()
def get_menu_items():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM menu_items")
            menu_items = cursor.fetchall()
    return jsonify({"menu_items": menu_items})


@app.post("/add_menu")
@cross_origin()
def add_menu():
    data = request.get_json()
    restaurant_id = data["restaurant_id"]
    items = data["items"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                ADD_MENU,
                (
                    restaurant_id,
                    items,
                ),
            )
            menu_id = cursor.fetchone()[0]

    return jsonify({"menu_id": menu_id})


@app.get("/get_menu_by_id")
@cross_origin()
def get_menu_by_id():
    data = request.get_json()
    restaurant_id = data["restaurant_id"]
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM menus WHERE restaurant_id = %s", (restaurant_id,)
            )
            menu = cursor.fetchone()
            menu_items = menu[2]
    return jsonify({"menu_items": menu_items})


if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5003)
