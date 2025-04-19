import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from controllers.parser_controller import extract_text_from_pdf
from db import summaries_collection, client  # Importing the collection and client

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
client_ai = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

# System prompt stays here
system_prompt = """
You are a highly knowledgeable Marvel Cinematic Universe expert assistant working with a team of MCU writers.
Your job is to evaluate creative inputs, spot canon contradictions, and generate a contradiction score (0–100). 
You will always respond in a structured JSON format, optionally calling functions when needed.

Rules:
- You are concise and direct.
- You point out inconsistencies in character traits, timelines, or known events from MCU canon (film, series, animation).
- You output in this exact JSON format:
- You generate a contradiction score from 0 to 100:
   - 0–10: Fully consistent with MCU canon
   - 11–40: Minor inconsistencies that could be explained
   - 41–70: Noticeable contradictions needing rewrites or fixes
   - 71–100: Major contradictions that break canon significantly

{
  "summary": "<Short one-liner summary>",
  "contradiction_score": <0 to 100>,
  "justification": [
    "<Point 1>",
    "<Point 2>"
  ],
  "recommendations": [
    "<Fix or suggestion if any>"
  ],
  "function_call": {
    "name": "<function_name_if_any>",
    "arguments": {
      "key": "value"
    }
  }
}

Only include "function_call" if needed.
You can call functions such as:
- flag_character_behavior(character: str, traits: list)
- timeline_check(event: str)
- suggest_explanation(contradiction: str)

Respond in JSON only — no extra commentary.
"""

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

app = Flask(__name__)

# Route to parse the PDF and run the AI model
@app.route('/parse', methods=['POST'])
def parse_pdf_and_run_ai():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_file = request.files['pdf']
    extracted_text = extract_text_from_pdf(pdf_file)

    if extracted_text.startswith("Error"):
        return jsonify({'error': extracted_text}), 500

    result = call_llm(extracted_text)
    return jsonify({'llm_response': result})

# Route to test MongoDB connection
@app.route('/db_status', methods=['GET'])
def db_status():
    try:
        client.admin.command('ping')
        return jsonify({"status": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "disconnected", "error": str(e)}), 500

# Test route to insert dummy data
@app.route('/test_insert', methods=['GET'])
def test_insert():
    dummy_data = {
        "title": "Test Movie",
        "script": "This is a test script for the dummy movie.",
        "timeline": "main",
        "created_by": "admin"
    }
    result = summaries_collection.insert_one(dummy_data)
    return jsonify({"message": "Data inserted", "inserted_id": str(result.inserted_id)})

# Test route to retrieve data
@app.route('/test_get', methods=['GET'])
def test_get():
    all_docs = summaries_collection.find()
    results = [{**doc, "_id": str(doc["_id"])} for doc in all_docs]
    return jsonify({"data": results})

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
