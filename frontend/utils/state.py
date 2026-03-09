
import streamlit as st

def init_state() :   # 안전한 기본 상태 보장 함수
    
    default_state = {
        "query" : "",                  # 사용자가 입력한 질문
        "videos" : [],                 # 추천된 영상 목록
        "selected_video_id" : None,    # 클릭한 영상 id
        "summary" : None,              # 영상 요약 내용
        "timeline" : [],               # 타임라인 정보
        "loading_recommend" : False,   # 추천 로딩 상태 (추천 API 기다리는 상태)
        "loading_summary" : False,     # 요약 로딩 상태 (요약 API 기다리는 상태)
        "error" : None                 # 에러 메시지
    }

    for key, value in default_state.items() :
        if key not in st.session_state :    # → 기존 데이터를 보호하는 안전장치
            st.session_state[key] = value
            # session_state → 사용자 세션 동안 유지되는 메모리 공간