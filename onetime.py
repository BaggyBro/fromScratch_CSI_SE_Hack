from pymongo import MongoClient
import spacy
from collections import defaultdict, OrderedDict
import re
from neo4j import GraphDatabase
import json

# Load NLP model
nlp = spacy.load("en_core_web_lg")

# MongoDB setup
client = MongoClient("mongodb+srv://tanishqchavan241:8lxUAOBVDRlTm44O@cluster0.9qe4xnl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["MCU"]
collection = db["main_summary"]

# Neo4j setup
NEO4J_URI = "neo4j+s://46659ffb.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "izPmjaBwAu6rVc6eLz2IFt25kyzEmoBjkaPeZ8BNvIs"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Clean Neo4j
with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    print("🧹 Existing Neo4j data wiped.")

# Known characters and locations for soft matching
known_characters = [
    "Tony Stark", "Iron Man", "Steve Rogers", "Captain America", "Thor", "Bruce Banner",
    "Hulk", "Natasha Romanoff", "Black Widow", "Clint Barton", "Hawkeye", "Loki",
    "Thanos", "Peter Parker", "Spider-Man", "Wanda Maximoff", "Scarlet Witch", "Vision",
    "Stephen Strange", "Doctor Strange", "T'Challa", "Black Panther", "Nick Fury", "Carol Danvers",
    "Captain Marvel", "Sam Wilson", "Falcon", "Bucky Barnes", "Winter Soldier"
]

known_locations = [
    "New York", "Asgard", "Wakanda", "Sokovia", "Titan", "Knowhere", "Xandar",
    "Earth", "Kamar-Taj", "Sanctum Sanctorum", "Avengers Tower", "Stark Tower", "Vormir"
]

# Timeline extraction
timeline = defaultdict(list)

def extract_year(text):
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return match.group(0) if match else None

def soft_match_entities(text, candidates):
    matches = []
    for candidate in candidates:
        if candidate.lower() in text.lower():
            matches.append(candidate)
    return list(set(matches))

for doc in collection.find():
    title = doc.get("title", "")
    summary = doc.get("summary", "")
    doc_nlp = nlp(summary)

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

        # Soft match known characters/locations
        matched_chars = soft_match_entities(sent.text, known_characters)
        matched_locs = soft_match_entities(sent.text, known_locations)
        characters.extend(matched_chars)
        locations.extend(matched_locs)

        if year:
            timeline[year].append({
                "title": title,
                "phrase": sent.text.strip(),
                "characters": list(set(characters)),  # deduplicate
                "locations": list(set(locations)),
                "universe": "Earth-199999",
                "confidence": 0.85,
                "version": "v1.0"
            })

# ✅ Convert timeline to simplified JSON
simple_timeline = []

for year, events in OrderedDict(sorted(timeline.items(), key=lambda x: int(x[0]))).items():
    for event in events:
        simple_timeline.append({
            "year": year,
            "event": event["phrase"]
        })

with open("mcu_timeline.json", "w", encoding="utf-8") as f:
    json.dump(simple_timeline, f, indent=2, ensure_ascii=False)

print("📁 Saved simplified MCU timeline as 'mcu_timeline.json'")

# Neo4j insert logic
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

# Push to Neo4j
with driver.session() as session:
    for year, entries in OrderedDict(sorted(timeline.items(), key=lambda x: int(x[0]))).items():
        for entry in entries:
            session.write_transaction(insert_event, year, entry)

print("✅ Full MCU timeline with rich entity modeling stored in Neo4j.")
driver.close()
