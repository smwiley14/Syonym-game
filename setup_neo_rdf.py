from neo4j import GraphDatabase
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from rdflib import Graph
import dotenv
import os

dotenv.load_dotenv()

AURA_URI = os.getenv("AURA_URI")
AURA_USERNAME = os.getenv("AURA_USERNAME")
AURA_PWD = os.getenv("AURA_PASSWORD")
ttl_path = "file:///Users/sam/Downloads/english-wordnet-2025.ttl"


auth_data = {'uri': AURA_URI,
             'database': AURA_USERNAME,
             'user': AURA_USERNAME,
             'pwd': AURA_PWD}


config = Neo4jStoreConfig(auth_data=auth_data,
                          custom_prefixes={},
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.IGNORE,
                          batching=True)


neo4j_aura = Graph(store=Neo4jStore(config=config))
neo4j_aura.parse(ttl_path, format="ttl")
neo4j_aura.close(True)