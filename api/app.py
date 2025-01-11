import os
import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS, cross_origin
from prometheus_client import Counter, generate_latest


ADD_RESTAURANT = "INSERT INTO restaurants (name, type, rating, address, average_time, price_range, image) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id"
ADD_MENU_ITEM = (
    "INSERT INTO menu_items (name, price, image) VALUES (%s, %s, %s) RETURNING id"
)
ADD_MENU = "INSERT INTO menus (restaurant_id, items) VALUES (%s, %s) RETURNING id"
load_dotenv()

app = Flask(__name__)
cors = CORS(app)

# Example metric: A counter for requests
REQUEST_COUNT = Counter('request_count', 'Total number of requests')

@app.route('/')
def home():
    REQUEST_COUNT.inc()  
    return "Welcome to the Restaurant Manager!"

# Expose /metrics for Prometheus
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), content_type='text/plain')

def check_database_connection():
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute('SELECT 1')  # Simple query to check if the database is responsive
        connection.close()
        print("Database is connected!")
    except OperationalError as err:
        raise Exception("Database is not reachable: " + str(err))

@app.route('/health')
def health_check():
    try:
        check_database_connection()
        return "Service is healthy", 200
    except:
        return "Service is unhealthy", 500


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
                    requests.get("https://foodish-api.com/api/").json()["image"],
                ),
            )
            res_id = cursor.fetchone()[0]

    requests.post(
        f"{os.getenv('AUTH_ENDPOINT')}/api/link_restaurant",
        json={"restaurant_id": res_id, "user_id": data["user_id"]},
        headers={"Content-Type": "application/json"}
    )

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
    image = requests.get("https://foodish-api.com/api/").json()["image"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                ADD_MENU_ITEM,
                (name, price, image),
            )
            menu_item_id = cursor.fetchone()[0]

    return jsonify({"menu_item": [menu_item_id, name, price, image]})


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
    restaurant_id = request.args.get("restaurant_id")
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM menus WHERE restaurant_id = %s", (restaurant_id,)
            )
            menu = cursor.fetchone()
            menu_items = menu[2]
            menu_items_data = []
            for item in menu_items:
                cursor.execute("SELECT * FROM menu_items WHERE id = %s", (item,))
                menu_items_data.append(cursor.fetchone())
    return jsonify({"menu_items": menu_items_data})


if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5003)
