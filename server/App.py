from flask import Flask
from handlers.orders_handler import order_bp
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)
db = client.get_default_database()

order_bp.db = db

app.register_blueprint(order_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(8080),debug=True)
