import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from controllers.parser_controller import extract_text_from_pdf
from db import summaries_collection, client  # MongoDB
from controllers.graphql_controller import graphql_bp
from controllers.vector_search_controller import vector_search_bp
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# OpenRouter AI client setup
api_key = os.getenv("OPENROUTER_API_KEY")
client_ai = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

# Initialize the Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Smaller, faster model

# 🚀 Embed the text using SentenceTransformer
def embed_text(text):
    return model.encode(text).tolist()  # Convert the text to a vector and return as a list

# 🌍 Canon data loader from MongoDB
def get_canon_context_from_vector_search(user_story_vector, limit=5):
    try:
        # Set up MongoDB aggregation pipeline for KNN search
        pipeline = [
            {
                "$search": {
                    "index": "default",  # Ensure this matches the name of your Atlas Search index
                    "knnBeta": {
                        "vector": user_story_vector,
                        "path": "embedding",  # Path to the embedding field in your MongoDB collection
                        "k": limit  # Number of nearest neighbors you want to retrieve
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

        # Execute the aggregation pipeline to get the most relevant canon data
        canon_results = list(summaries_collection.aggregate(pipeline))
        return canon_results
    except Exception as e:
        return f"Error fetching canon context: {e}"

# 🤖 LLM System Prompt (Updated for function call)
system_prompt = """
You are a highly knowledgeable Marvel Cinematic Universe expert assistant working with a team of MCU writers.
Your job is to evaluate creative inputs, spot canon contradictions, and generate a contradiction score (0–100). 
You will always respond in this structured JSON format:

{
  "summary": "<Short one-liner summary>",
  "contradiction_score": <0 to 100>,
  "justification": [
    "<Point 1>",
    "<Point 2>"
  ],
  "recommendations": [
    "<Fix or suggestion if any>"
  ]
}

Your evaluation should consider contradictions in character traits, timelines, or events based on MCU canon (films, series, animation).

Only call a function if you need further clarification or data, and use the function call format if needed. If the contradictions are clear and do not need any more context, just respond with your analysis and recommendation.

Do not use unnecessary function calls. Only evaluate based on the data provided and provide clear, actionable insights.
"""

# 🧠 Main function to call LLM
def call_llm(prompt, model="meta-llama/llama-4-maverick:free"):
    try:
        response = client_ai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling LLM: {e}"

# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Register blueprints
app.register_blueprint(graphql_bp)
app.register_blueprint(vector_search_bp, url_prefix='/vector_search')

# 📄 Route: Upload a story, compare with canon, get contradiction report
@app.route('/parse', methods=['POST'])
def parse_pdf_and_run_ai():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    # Extract text from the uploaded PDF
    pdf_file = request.files['pdf']
    extracted_text = extract_text_from_pdf(pdf_file)

    if extracted_text.startswith("Error"):
        return jsonify({'error': extracted_text}), 500

    # Step 1: Embed the extracted user text (story) into a vector
    user_story_vector = embed_text(extracted_text)

    # Step 2: Perform Vector Search on MongoDB for the most relevant canon data
    canon_results = get_canon_context_from_vector_search(user_story_vector, limit=5)
    
    # Step 3: Prepare the context for the LLM
    canon_context = "\n".join([f"Title: {result['title']}\nSummary: {result['summary']}" for result in canon_results])
    
    # Combine the user story and canon context
    prompt = f"""
    MCU Canon:
    {canon_context}

    --- USER INPUT BELOW ---

    New Story Submission:
    {extracted_text}

    Evaluate the user input against MCU canon.
    """

    # Step 4: Call the LLM with the combined prompt
    llm_result = call_llm(prompt)

    return jsonify({'llm_response': llm_result})

# ✅ Route to check MongoDB status
@app.route('/db_status', methods=['GET'])
def db_status():
    try:
        client.admin.command('ping')
        return jsonify({"status": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "disconnected", "error": str(e)}), 500

# 🔍 Route to get all MongoDB inputs
@app.route('/get_all_inputs', methods=['GET'])
def get_all_inputs():
    try:
        all_docs = summaries_collection.find()
        results = [{**doc, "_id": str(doc["_id"])} for doc in all_docs]
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
