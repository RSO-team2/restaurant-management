import os
import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS, cross_origin
from prometheus_flask_exporter import PrometheusMetrics


ADD_RESTAURANT = "INSERT INTO restaurants (name, type, rating, address, average_time, price_range, image) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id"
ADD_MENU_ITEM = (
    "INSERT INTO menu_items (name, price, image) VALUES (%s, %s, %s) RETURNING id"
)
ADD_MENU = "INSERT INTO menus (restaurant_id, items) VALUES (%s, %s) RETURNING id"
load_dotenv()

app = Flask(__name__)
cors = CORS(app)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Restaurant Management API Info', version='1.0.0')

def check_database_connection():
     """
    Checks if the database connection is active and operational.
    Raises an exception if the database is not reachable.
    """
    try:
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute('SELECT 1') 
        connection.close()
        print("Database is connected!")
    except OperationalError as err:
        raise Exception("Database is not reachable: " + str(err))

@app.route('/health')
def health_check():
    """
    Health check endpoint to verify if the service and database are operational.
    Returns HTTP 200 if healthy, otherwise HTTP 500.
    """
    try:
        check_database_connection()
        return "Service is healthy", 200
    except:
        return "Service is unhealthy", 500


@app.post("/add_restaurant")
@cross_origin()
def add_restaurant():
     """
    Add a new restaurant to the database.
    Fetches data from the request body, adds a restaurant entry, and links it to a user.
    """
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
    """
    Fetch all restaurants from the database.
    """
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM restaurants")
            restaurants = cursor.fetchall()

    return jsonify({"resturant_list": restaurants})


@app.post("/add_menu_item")
@cross_origin()
def add_menu_item():
    """
    Add a new menu item to the database.
    Fetches data from the request body and inserts a menu item with a random image.
    """
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
    """
    Fetch all menu items from the database.
    """
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM menu_items")
            menu_items = cursor.fetchall()
    return jsonify({"menu_items": menu_items})


@app.post("/add_menu")
@cross_origin()
def add_menu():
    """
    Add a menu to a restaurant.
    Fetches restaurant ID and menu items from the request body, then inserts the menu.
    """
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
    """
    Fetch the menu for a specific restaurant by its ID.
    Queries the database for the menu and its associated items.
    """
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
