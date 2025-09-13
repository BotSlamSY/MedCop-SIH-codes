import requests
import json

BASE_URL = "http://localhost:8000"


def test_webhook(query_text, intent="", disease=""):
    payload = {
        "queryResult": {
            "queryText": query_text,
            "intent": {
                "displayName": intent
            },
            "parameters": {
                "disease": disease
            }
        },
        "session": "test-session-interactive"
    }

    response = requests.post(f"{BASE_URL}/webhook", json=payload)

    if response.status_code == 200:
        result = response.json()
        print(f"Query: {query_text}")
        print(f"Response: {result.get('fulfillmentText', 'No response')}")
        print("-" * 50)
    else:
        print(f"Error: {response.status_code} - {response.text}")


# Test various queries
if __name__ == "__main__":
    print("Testing Healthcare Chatbot...\n")

    # Test cases
    test_cases = [
        ("malaria symptoms", "symptoms.query", "malaria"),
        ("मलेरिया के लक्षण", "symptoms.query", "malaria"),
        ("how to prevent dengue", "prevention.query", "dengue"),
        ("dengue se kaise bachen", "prevention.query", "dengue"),
        ("vaccination information", "vaccination.query", ""),
        ("emergency contacts", "emergency.query", ""),
        ("covid data india", "health.data.query", ""),
        ("fever headache nausea", "", ""),  # Test ML matching
        ("hello", "", ""),  # Test default response
    ]

    for query, intent, disease in test_cases:
        test_webhook(query, intent, disease)
