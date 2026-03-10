
import streamlit as st

def init_state():   # 안전한 기본 상태 보장 함수
    
    default_state = {
        "query": "",
        "videos": [],
        "selected_video_id": None,
        "summary": None,
        "timeline": [],
        "loading_recommend": False,
        "loading_summary": False,
        "error": None,
        "lecture_note": None,
        "quiz_data": None,
        "active_tab": "summary",
        "last_summary_id": None   # 🔥 반드시 추가
    }

    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value