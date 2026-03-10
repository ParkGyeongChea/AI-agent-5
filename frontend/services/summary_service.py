import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# ==========================================================
# 1️⃣ Summary
# ==========================================================

def fetch_summary(video_id: str):

    try:
        r = requests.post(
            f"{BACKEND_URL}/test/video/info/full/{video_id}",
            timeout=20
        )

        # 🔥 백엔드 데이터 없는 경우 fallback 처리
        if r.status_code != 200:

            return {
                "data": {
                    "summary": "해당 영상의 Summary 데이터가 아직 준비되지 않았습니다.",
                    "timeline": [],
                    "transcribe": {"transcript": []}
                },
                "error": None
            }

        return {
            "data": r.json(),
            "error": None
        }

    except Exception:

        return {
            "data": {
                "summary": "요약 데이터를 불러올 수 없습니다.",
                "timeline": [],
                "transcribe": {"transcript": []}
            },
            "error": None
        }


# ==========================================================
# 2️⃣ Lecture Note
# ==========================================================

def fetch_lecture_note(video_id: str):

    try:
        r = requests.post(
            f"{BACKEND_URL}/test/video/service/lecture-note/{video_id}",
            timeout=30
        )

        if r.status_code != 200:
            return {
                "data": {
                    "learning_objectives": [],
                    "table_of_contents": []
                },
                "error": None
            }

        return {
            "data": r.json(),
            "error": None
        }

    except Exception:

        return {
            "data": {
                "learning_objectives": [],
                "table_of_contents": []
            },
            "error": None
        }


# ==========================================================
# 3️⃣ Quiz
# ==========================================================

def fetch_quiz(video_id: str):

    try:
        r = requests.post(
            f"{BACKEND_URL}/test/video/service/quiz/{video_id}",
            timeout=30
        )

        if r.status_code != 200:
            return {
                "data": {
                    "questions": []
                },
                "error": None
            }

        return {
            "data": r.json(),
            "error": None
        }

    except Exception:

        return {
            "data": {
                "questions": []
            },
            "error": None
        }