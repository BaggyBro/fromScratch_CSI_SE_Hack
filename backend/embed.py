from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ MONGO_URI is not set in the environment variables.")
    exit(1)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
collection = client["MCU"]["main_summary"]

# Load a FREE embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dims

# Go over each doc and store embedding
for doc in collection.find():
    summary = doc.get("summary", "")
    if summary:
        # Generate embedding for the summary
        embedding = model.encode(summary).tolist()
        
        # Update the document with the embedding
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"embedding": embedding}}
        )
        print(f"✅ Embedding added for document ID: {doc['_id']}")
    else:
        print(f"❌ No summary found for document ID: {doc['_id']}")
