import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def fetch_recommend(query: str):

    try:
        r = requests.post(
            f"{BACKEND_URL}/test/video/{query}",
            timeout=10
        )

        if r.status_code != 200:
            return {
                "data": None,
                "error": {
                    "type": "BACKEND_ERROR",
                    "message": r.text,
                    "retryable": False
                }
            }

        return {
            "data": {"videos": r.json()},
            "error": None
        }

    except Exception as e:
        return {
            "data": None,
            "error": {
                "type": "CONNECTION_ERROR",
                "message": str(e),
                "retryable": True
            }
        }