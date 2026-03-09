import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def fetch_summary(video_id: str):

    try:
        r = requests.post(
            f"{BACKEND_URL}/test/video/info/full/{video_id}",
            timeout=20
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
            "data": r.json(),
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