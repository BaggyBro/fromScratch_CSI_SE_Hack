from pymongo import MongoClient
import spacy
from collections import defaultdict, OrderedDict
import re
from neo4j import GraphDatabase

# Load NLP model (use a larger model for better entity recognition)
nlp = spacy.load("en_core_web_lg")  # or "en_core_web_lg"

# MongoDB setup
client = MongoClient("mongodb+srv://tanishqchavan241:8lxUAOBVDRlTm44O@cluster0.9qe4xnl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["MCU"]
collection = db["main_summary"]

# Neo4j setup
NEO4J_URI = "neo4j+s://46659ffb.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "izPmjaBwAu6rVc6eLz2IFt25kyzEmoBjkaPeZ8BNvIs"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Step 1: Wipe all existing data in Neo4j
with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    print("🧹 Existing Neo4j data wiped.")

# Step 2: Extract timeline from MongoDB
timeline = defaultdict(list)

def extract_year(text):
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return match.group(0) if match else None

for doc in collection.find():
    title = doc.get("title", "")
    summary = doc.get("summary", "")
    doc_nlp = nlp(summary)

    # Print out all the entities detected
    print(f"Movie: {title}")
    for ent in doc_nlp.ents:
        print(f"Entity: {ent.text}, Label: {ent.label_}")

    for sent in doc_nlp.sents:
        year = None
        characters = []
        locations = []
        for ent in sent.ents:
            if ent.label_ == "DATE" and not year:
                year = extract_year(ent.text)
            elif ent.label_ == "PERSON":
                characters.append(ent.text)
            elif ent.label_ == "GPE":
                locations.append(ent.text)

        if year:
            timeline[year].append({
                "title": title,
                "phrase": sent.text.strip(),
                "characters": characters,
                "locations": locations,
                "universe": "Earth-199999",
                "confidence": 0.85,
                "version": "v1.0"
            })

# Step 3: Neo4j insert logic (same as before)
def insert_event(tx, year, event_data):
    tx.run("""
        MERGE (y:Year {value: $year})
        MERGE (m:Movie {title: $movie})
        CREATE (e:Event {
            description: $event,
            confidence: $confidence,
            version: $version
        })
        MERGE (u:Universe {name: $universe})
        MERGE (e)-[:OCCURS_IN]->(y)
        MERGE (e)-[:MENTIONED_IN]->(m)
        MERGE (e)-[:IN_UNIVERSE]->(u)
        FOREACH (char IN $characters |
            MERGE (c:Character {name: char})
            MERGE (e)-[:INVOLVES]->(c)
        )
        FOREACH (loc IN $locations |
            MERGE (l:Location {name: loc})
            MERGE (e)-[:SET_IN]->(l)
        )
    """, year=year,
         event=event_data["phrase"],
         movie=event_data["title"],
         confidence=event_data["confidence"],
         version=event_data["version"],
         universe=event_data["universe"],
         characters=event_data["characters"],
         locations=event_data["locations"]
    )

# Step 4: Push data to Neo4j (same as before)
with driver.session() as session:
    for year, entries in OrderedDict(sorted(timeline.items(), key=lambda x: int(x[0]))).items():
        for entry in entries:
            session.write_transaction(insert_event, year, entry)

print("✅ Fictional timeline with detailed world modeling stored in Neo4j.")

# Close Neo4j connection
