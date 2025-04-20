# db.py

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

# Ping the database to confirm connection
try:
    client.admin.command('ping')
    print("✅ MongoDB connection successful.")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

db = client["MCU"]

summaries_collection = db["main_summary"]
reports_collection = db["reports"]
script_collection = db["scripts"]
