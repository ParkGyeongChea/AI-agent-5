# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st
from services.summary_service import (
    fetch_summary,
    fetch_lecture_note,
    fetch_quiz
)

# ==========================================================
# 2️⃣ 요약 패널 렌더링 함수
# ==========================================================

def render_summary_panel():

    selected_id = st.session_state.get("selected_video_id")

    if not selected_id:
        return

    # 🔥 영상 변경 감지 (핵심 수정)
    if st.session_state.last_summary_id != selected_id:

        st.session_state.summary = None
        st.session_state.lecture_note = None
        st.session_state.quiz_data = None

        st.session_state.last_summary_id = selected_id
        st.session_state.active_tab = "summary"

    st.markdown("## 📚 학습 내용 정리")

    # ======================================================
    # 탭 버튼 영역
    # ======================================================

    st.markdown(
        """
        <style>
        .tab-btn button {
            width: 100%;
            font-size: 15px;
            font-weight: 500;
            padding: 8px 0px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="tab-btn">', unsafe_allow_html=True)
        if st.button("Summary", use_container_width=True):
            st.session_state.active_tab = "summary"
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="tab-btn">', unsafe_allow_html=True)
        if st.button("Lecture Note", use_container_width=True):
            st.session_state.active_tab = "lecture"
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="tab-btn">', unsafe_allow_html=True)
        if st.button("Quiz", use_container_width=True):
            st.session_state.active_tab = "quiz"
        st.markdown('</div>', unsafe_allow_html=True)

    active_tab = st.session_state.get("active_tab", "summary")

    # ======================================================
    # SUMMARY
    # ======================================================

    if active_tab == "summary":

        if st.session_state.summary is None:

            with st.spinner("영상 내용을 분석 중입니다..."):
                result = fetch_summary(selected_id)

            if result["error"]:
                st.error(result["error"]["message"])
                return

            st.session_state.summary = result["data"]

        summary_data = st.session_state.summary

        st.markdown("### 📝 Summary")
        st.info(summary_data.get("summary", ""))

        st.markdown("---")

        st.markdown("### ⏱️ Timeline")

        for item in summary_data.get("timeline", []):
            st.markdown(f"**{item.get('time', '')}**")
            st.markdown(item.get("summary", ""))
            st.markdown("")

    # ======================================================
    # LECTURE NOTE
    # ======================================================

    elif active_tab == "lecture":

        if st.session_state.lecture_note is None:

            with st.spinner("강의 자료 생성 중..."):
                result = fetch_lecture_note(selected_id)

            if result["error"]:
                st.error(result["error"]["message"])
                return

            st.session_state.lecture_note = result["data"]

        note = st.session_state.lecture_note

        st.markdown("### 📘 강의 자료")

        st.subheader("🎯 학습 목표")

        for obj in note.get("learning_objectives", []):
            st.markdown(f"- {obj}")

        st.markdown("---")

        st.subheader("📚 목차")

        for toc in note.get("table_of_contents", []):
            st.markdown(f"- {toc}")

    # ======================================================
    # QUIZ
    # ======================================================

    elif active_tab == "quiz":

        if st.session_state.quiz_data is None:

            with st.spinner("퀴즈 생성 중..."):
                result = fetch_quiz(selected_id)

            if result["error"]:
                st.error(result["error"]["message"])
                return

            st.session_state.quiz_data = result["data"]

        quiz = st.session_state.quiz_data

        st.markdown("### 📝 퀴즈")

        for idx, q in enumerate(quiz.get("questions", []), 1):

            st.markdown(f"**Q{idx}. {q['question']}**")

            user_answer = st.radio(
                "정답 선택",
                q["options"],
                key=f"quiz_{selected_id}_{idx}",   # 🔥 영상별 key 분리
                index=None
            )

            if user_answer is not None:

                if user_answer == q["answer"]:
                    st.success("정답입니다!")

                else:
                    st.error("오답입니다. 다시 생각해보세요.")

            st.markdown("---")