
# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st
from services.summary_service import fetch_summary

# ==========================================================
# 2️⃣ 요약 패널 렌더링 함수
# ==========================================================

def render_summary_panel() :

    # ------------------------------------------------------
    # 2-1 선택된 영상이 없으면 렌더링 중단
    # ------------------------------------------------------

    selected_id = st.session_state.get("selected_video_id")

    if not selected_id :
        return
    
    # ------------------------------------------------------
    # 2-2 영상이 변경되었는지 확인
    # ------------------------------------------------------

    last_summary_id = st.session_state.get("last_summary_id")

    if last_summary_id != selected_id:
        st.session_state.summary = None
        st.session_state.last_summary_id = selected_id
    
    # ------------------------------------------------------
    # 2-3 summary가 아직 없는 경우 → fetch 호출
    # ------------------------------------------------------

    if st.session_state.summary is None:

        with st.spinner("영상 내용을 분석 중입니다..."):

            result = fetch_summary(selected_id)

        if result["error"]:
            st.error(result["error"]["message"])
            return
        else:
            # 상태 저장 → rerun 후 아래에서 사용
            st.session_state.summary = result["data"]
    
    # ======================================================
    # 3️⃣ UI 렌더링 시작
    # ======================================================

    summary_data = st.session_state.summary
    st.markdown("## 📚 학습 내용 정리")
    
    st.markdown("---")
    
    # ======================================================
    # 5️⃣ Summary 영역
    # ======================================================

    st.markdown("### 📝 Summary")

    st.info(summary_data["summary"])

    st.markdown("---")

    # ======================================================
    # 6️⃣ Key Points 영역 (카드형 UI)
    # ======================================================

    st.markdown("### 🧠 Key Points")

    key_points = summary_data.get(
        "key_points",
        [
            "핵심 개념 정리",
            "주의해야 할 실수"
        ]
    )

    for point in key_points:
        st.markdown(
            f"""
            <div style="
                padding:12px;
                border-radius:10px;
                background-color:#1f2937;
                margin-bottom:10px;
            ">
            ✅ {point}
            </div>
            """,
            unsafe_allow_html=True
        )
            
    st.markdown("---")


    # ======================================================
    # 7️⃣ Timeline 영역
    # ======================================================

    st.markdown("### ⏱️ Timeline")
    
    # timeline도 상태 기반으로 확장 예정
    timeline_data = summary_data["timeline"]

    for item in timeline_data:
        st.markdown(f"**{item['time']}**")
        st.markdown(item["text"])
        st.markdown("")

    st.markdown("---")

    # ======================================================
    # 8️⃣ 학습 액션 영역
    # ======================================================

    st.markdown("### 📥 학습 액션")
    
    col1, col2 = st.columns(2)

    with col1:
        st.button("📄 요약 PDF 다운로드")

    with col2:
        st.button("🎧 음성 파일 다운로드")