# ==========================================================
# 1️⃣ 필요한 모듈 import
# ==========================================================

import streamlit as st
from services.recommend_service import fetch_recommend


# ==========================================================
# 2️⃣ 검색 UI 렌더링 함수 정의
# ==========================================================

def render_search():

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
    # 버튼 클릭
    # ------------------------------------------------------

    if st.button("관련 영상 추천 받기 💌"):

        if not query.strip():
            st.warning("검색어를 입력해주세요.")
            return

        with st.spinner("AI가 영상을 분석 중입니다..."):
            result = fetch_recommend(query)

        # ------------------------------------------------------
        # 오류 발생
        # ------------------------------------------------------

        if result["error"]:

            st.session_state.videos = []
            st.session_state.error = result["error"]["message"]

        # ------------------------------------------------------
        # 정상 응답
        # ------------------------------------------------------

        else:

            st.session_state.error = None
            st.session_state.videos = result["data"]["videos"]

            # 검색어 저장
            st.session_state.query = query

            # --------------------------------------------------
            # 첫 영상 자동 선택
            # --------------------------------------------------

            if result["data"]["videos"]:

                first_video = result["data"]["videos"][0]

                # 선택 영상 설정
                st.session_state.selected_video_id = first_video["video_id"]

                # 상태 초기화 (핵심 수정)
                st.session_state.summary = None
                st.session_state.timeline = []
                st.session_state.lecture_note = None
                st.session_state.quiz_data = None
                st.session_state.last_summary_id = None
                st.session_state.active_tab = "summary"
                st.session_state.error = None

                # 페이지 재실행
                st.rerun()