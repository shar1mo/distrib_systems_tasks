# app/client.py
import requests

PROJECT_CODE = "sessions-s13"

GRAPHQL_URL = "http://localhost:8107/graphql"  # ваш endpoint

def build_payload(query: str, variables: dict) -> dict:
    return {
        "query": query,
        "variables": variables
    }

def run_query():
    query = """
    query {
        sessions {
            id
            ip
        }
    }
    """
    payload = build_payload(query, {})
    response = requests.post(GRAPHQL_URL, json=payload)
    result = response.json()
    if "errors" in result:
        print("Query errors:", result["errors"])
    else:
        print("Query data:", result["data"])

def run_mutation():
    mutation = """
    mutation($ip: String!) {
        createSession(ip: $ip) {
            id
            ip
        }
    }
    """
    variables = {"ip": "192.168.1.1"}
    payload = build_payload(mutation, variables)
    response = requests.post(GRAPHQL_URL, json=payload)
    result = response.json()
    if "errors" in result:
        print("Mutation errors:", result["errors"])
    else:
        print("Mutation data:", result["data"])


if __name__ == "__main__":
    print("Running Query...")
    run_query()
    print("\nRunning Mutation...")
    run_mutation()