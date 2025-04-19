from flask import Blueprint, request, jsonify
from graphene import ObjectType, String, Schema, Field, List
from neo4j import GraphDatabase

# Blueprint for modularity
graphql_bp = Blueprint("graphql_bp", __name__)

# Neo4j setup
driver = GraphDatabase.driver(
    "neo4j+s://46659ffb.databases.neo4j.io",
    auth=("neo4j", "izPmjaBwAu6rVc6eLz2IFt25kyzEmoBjkaPeZ8BNvIs")
)

# GraphQL Object Types
class NodeType(ObjectType):
    label = String()
    name = String()

class RelationshipType(ObjectType):
    start_node = Field(NodeType)
    end_node = Field(NodeType)
    type = String()

class Query(ObjectType):
    all_relationships = List(RelationshipType)

    def resolve_all_relationships(root, info):
        with driver.session() as session:
            result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN labels(a)[0] AS a_label, a.name AS a_name,
                       labels(b)[0] AS b_label, b.name AS b_name,
                       type(r) AS rel_type
                LIMIT 100
            """)
            return [
                RelationshipType(
                    start_node=NodeType(label=record["a_label"], name=record["a_name"]),
                    end_node=NodeType(label=record["b_label"], name=record["b_name"]),
                    type=record["rel_type"]
                ) for record in result
            ]

schema = Schema(query=Query)

@graphql_bp.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    result = schema.execute(data.get("query"))
    return jsonify(result.data)
