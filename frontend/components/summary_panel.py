# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st
from services.summary_service import fetch_summary


# ==========================================================
# 2️⃣ 요약 패널 렌더링 함수
# ==========================================================

def render_summary_panel():

    selected_id = st.session_state.get("selected_video_id")

    if not selected_id:
        return

    # 영상 변경 감지
    last_summary_id = st.session_state.get("last_summary_id")

    if last_summary_id != selected_id:
        st.session_state.summary = None
        st.session_state.last_summary_id = selected_id

    # summary 없으면 fetch
    if st.session_state.summary is None:

        with st.spinner("영상 내용을 분석 중입니다..."):
            result = fetch_summary(selected_id)

        if result["error"]:
            st.error(result["error"]["message"])
            return

        st.session_state.summary = result["data"]

    # ======================================================
    # 3️⃣ UI 렌더링
    # ======================================================

    summary_data = st.session_state.summary

    st.markdown("## 📚 학습 내용 정리")
    st.markdown("---")

    # ======================================================
    # Summary
    # ======================================================

    st.markdown("### 📝 Summary")
    st.info(summary_data.get("summary", ""))

    st.markdown("---")

    # ======================================================
    # Timeline
    # ======================================================

    st.markdown("### ⏱️ Timeline")

    timeline_data = summary_data.get("timeline", [])

    for item in timeline_data:
        st.markdown(f"**{item.get('time', '')}**")
        st.markdown(item.get("summary", ""))
        st.markdown("")

    st.markdown("---")

    # ======================================================
    # 학습 액션 영역
    # ======================================================

    st.markdown("### 📥 학습 액션")

    col1, col2 = st.columns(2)

    with col1:
        st.button("📄 요약 PDF 다운로드")

    with col2:
        st.button("🎧 음성 파일 다운로드")