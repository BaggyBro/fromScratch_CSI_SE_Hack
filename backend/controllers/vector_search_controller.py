from flask import Blueprint, request, jsonify
from sentence_transformers import SentenceTransformer
from db import summaries_collection
from tqdm import tqdm

# Initialize the blueprint
vector_search_bp = Blueprint('vector_search', __name__)
commit_bp = Blueprint("commit_bp", __name__)

# Initialize the Sentence Transformer model (same as before)
model = SentenceTransformer("all-MiniLM-L6-v2")  # You can change the model to something else

# Function to embed a query text
def embed_text(text):
    return model.encode(text).tolist()

# 🚀 Route: Vector Search
@vector_search_bp.route('/search', methods=['POST'])
def vector_search():
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Generate embedding for the query
    query_vector = embed_text(query)

    # Set up MongoDB aggregation pipeline for KNN search
    pipeline = [
        {
            "$search": {
                "index": "default",  # Ensure this matches the name of your Atlas Search index
                "knnBeta": {
                    "vector": query_vector,
                    "path": "embedding",  # Path to the embedding field in your MongoDB collection
                    "k": 5  # Number of nearest neighbors you want to retrieve
                }
            }
        },
        {
            "$project": {
                "title": 1,
                "summary": 1,
                "_id": 0,
                "score": {"$meta": "searchScore"}  # Include the search score
            }
        }
    ]

    # Execute the aggregation pipeline
    results = list(summaries_collection.aggregate(pipeline))
    return jsonify({"results": results})
