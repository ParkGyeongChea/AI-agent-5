
# ==========================================================
# 1️⃣ 필요한 모듈 import
# ==========================================================

import streamlit as st  # Streamlit UI 라이브러리
from services.recommend_service import fetch_recommend

# ==========================================================
# 2️⃣ 검색 UI 렌더링 함수 정의
# ==========================================================

def render_search() :

    # ------------------------------------------------------
    # 2-1 사용자 입력 받기
    # ------------------------------------------------------
    
    st.markdown(
        """
        <h3 style="margin-bottom:6px;">
            학습 주제를 입력하세요 ✍🏻
        </h3>
        """,
        unsafe_allow_html=True
    )

    query = st.text_input(
        "학습 주제",
        placeholder="예 : Python 기초, LangChain 활용, FastAPI 개발 등",
        label_visibility="collapsed"
    )

    # ------------------------------------------------------
    # 2-2 버튼 클릭 감지
    # ------------------------------------------------------
    
    if st.button("관련 영상 추천 받기 💌") :
        
        # --------------------------------------------------
        # 2-3 Spinner 사용 이유
        # --------------------------------------------------
        
        with st.spinner("AI가 영상을 분석 중입니다...") :
            
            # --------------------------------------------------
            # 2-4 서비스 호출
            # --------------------------------------------------
            
            result = fetch_recommend(query)
        
        # --------------------------------------------------
        # 2-5 반환 구조 처리
        # --------------------------------------------------
        
        if result["error"] :
            
            # 실패 시
            # --------------------------------------------------
            st.session_state.videos = []
            st.session_state.error = result["error"]["message"]
        
        else :
            
            # 성공 시
            # --------------------------------------------------
            st.session_state.error = None
            st.session_state.videos = result["data"]["videos"]
            
            # 검색어 저장
            st.session_state.search_query = query
            
            # --------------------------------------------------
            # 추천 직후 첫 번째 영상 자동 선택
            # --------------------------------------------------
            
            if result["data"]["videos"] :
                st.session_state.selected_video_id = result["data"]["videos"][0]["id"]
                st.session_state.summary = None
                st.session_state.timeline = []