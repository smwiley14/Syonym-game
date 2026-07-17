import csv
import os
import sys
from neo4j import GraphDatabase

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]
csv_path = sys.argv[1] if len(sys.argv) > 1 else "conceptnet_game_ready.csv"

BATCH_SIZE = 500

driver = GraphDatabase.driver(uri, auth=(username, password))

def import_batch(session, batch):
    session.run("""
        UNWIND $rows AS row
        MERGE (a:ConceptNetNode {term: row.start})
        MERGE (b:ConceptNetNode {term: row.end})
        CREATE (a)-[:CN_REL {type: row.rel, weight: row.weight}]->(b)
    """, rows=batch)

with driver.session() as session:
    batch = []
    total = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({
                "start": row["start"],
                "end": row["end"],
                "rel": row["rel"],
                "weight": float(row["weight"]),
            })
            if len(batch) >= BATCH_SIZE:
                import_batch(session, batch)
                total += len(batch)
                print(f"Imported {total} rows...", flush=True)
                batch = []
        if batch:
            import_batch(session, batch)
            total += len(batch)

    print(f"Done. Total rows imported: {total}")

driver.close()
