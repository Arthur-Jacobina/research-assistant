import os
from neo4j import GraphDatabase

neo4j_url = os.getenv('NEO4J_URL', 'neo4j://localhost:7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'your_password')


driver = GraphDatabase.driver(
    neo4j_url,
    auth=(neo4j_user, neo4j_password)
)