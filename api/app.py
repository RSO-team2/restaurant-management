import os
import psycopg2
import bcrypt
import asyncio
from nats.aio.client import Client as NATS
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request, jsonify

app = Flask(__name__)

if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5001)