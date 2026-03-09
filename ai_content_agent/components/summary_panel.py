"""
summary_panel.py

이 파일은 "우측 학습 리포트 패널"을 렌더링하는 UI 컴포넌트이다

1. 선택된 영상(selected_video_id) 상태를 읽는다
2. 요약 데이터 (summary, timeline)를 읽는다
3. 학습 리포트를 구조화하여 화면에 출력한다
4. UI는 데이터를 가공하지 않는다 (읽기 전용)

[중요 설계 원칙]
- 상태 기반 UI (State Driven UI)
- UI는 session_state를 읽기만 한다
- 상태 변경은 다른 컴포넌트에서 발생한다
- 이 파일은 "표현 계층(View Layer)"이다

[데이터 흐름]
video_list.py
    ↓ (selected_video_id 변경)
session_state.selected_video_id
    ↓
summary_service 호출 (추후 연결)
    ↓
session_state.summary / timeline 저장
    ↓
이 패널이 읽어서 렌더링
"""

# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st
# Streamlit UI 라이브러리
# 이 파일은 UI 렌더링만 담당한다

from services.summary_service import fetch_summary

# ==========================================================
# 2️⃣ 요약 패널 렌더링 함수
# ==========================================================

def render_summary_panel() :
    """
    우측 학습 리포트 패널 렌더링 함수
    
    이 함수는 다음 상태를 읽는다 :
    
    - selected_video_id
    - summary
    - timeline
    
    상태가 없으면 아무것도 렌더링하지 않는다
    
    Streamlit은 rerun 구조이기 때문에
    상태 기반 조건부 렌더링이 중요하다
    """
    
    # ------------------------------------------------------
    # 2-1 선택된 영상이 없으면 렌더링 중단
    # ------------------------------------------------------
    # selected_video_id는 영상 선택 시 저장된다
    # None이면 아직 선택되지 않은 상태
    # ------------------------------------------------------

    selected_id = st.session_state.get("selected_video_id")

    if not selected_id :
        # 아무 영상도 선택되지 않은 경우
        # 패널을 렌더링하지 않는다
        return
    
    # ------------------------------------------------------
    # 2-2 영상이 변경되었는지 확인
    # ------------------------------------------------------
    # last_summary_id와 비교하여
    # 영상이 바뀌면 summary 초기화
    # ------------------------------------------------------

    last_summary_id = st.session_state.get("last_summary_id")

    if last_summary_id != selected_id:
        st.session_state.summary = None
        st.session_state.last_summary_id = selected_id
    
    # ------------------------------------------------------
    # 2-3 summary가 아직 없는 경우 → fetch 호출
    # ------------------------------------------------------
    # Streamlit은 rerun 구조이므로
    # summary가 None일 때만 호출해야 한다.
    # 그렇지 않으면 매 rerun마다 API 호출됨
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
    
    # ------------------------------------------------------
    # UI는 여기서부터 순차적으로 구성된다
    # 메타 정보 → Summary → Key Points → Timeline → Action
    # ------------------------------------------------------
    
    # ======================================================
    # 4️⃣ 학습 메타 정보 영역
    # ======================================================
    
    # st.markdown("### 📊 학습 메타 정보")
    
    # # 3컬럼 레이아웃 생성
    # # → 정보 밀도를 높이기 위해
    # # → KPI 대시보드 느낌을 주기 위해
    
    # col1, col2, col3 = st.columns(3)
    
    # # metric은 숫자/지표 표현에 적합
    # # 현재는 Mock 데이터이므로 고정 값 사용
    # col1.metric("난이도", "중급")
    # col2.metric("예상 학습 시간", "45분")
    # col3.metric("추천 대상", "입문자")

    # st.markdown("---")
    
    # ======================================================
    # 5️⃣ Summary 영역
    # ======================================================

    st.markdown("### 📝 Summary")
    
    # summary는 나중에 session_state에서 가져올 예정
    # 지금은 Mock 문자열 사용
    
    st.info(summary_data["summary"])
    
    # info 박스를 사용하는 이유
    # → 강조 영역 시각화
    # → 카드 느낌 제공

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