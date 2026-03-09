# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st


# ==========================================================
# 2️⃣ 텍스트 길이 제한 함수
# ==========================================================

def truncate_text(text: str, max_length: int):
    if not text:
        return ""

    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


# ==========================================================
# 3️⃣ 영상 목록 렌더링 함수
# ==========================================================

def render_video_list():

    # --------------------------------------------------
    # 3-1 추천 결과 없으면 종료
    # --------------------------------------------------

    if not st.session_state.videos:
        return

    videos = st.session_state.videos
    selected_id = st.session_state.get("selected_video_id")

    # --------------------------------------------------
    # 3-2 선택된 영상 맨 앞으로 정렬
    # --------------------------------------------------

    if selected_id:
        videos = sorted(
            videos,
            key=lambda v: v["video_id"] != selected_id
        )

    st.markdown("---")
    st.subheader("추천 영상 목록 🎬")

    # ======================================================
    # 4️⃣ 첫 번째 영상 (Hero 영역)
    # ======================================================

    main_video = videos[0]

    # 선택된 영상이면 플레이어 출력
    if selected_id == main_video["video_id"]:
        st.video(main_video["url"])
    else:
        st.image(main_video["thumbnail_url"], width="stretch")

    # 제목 출력
    st.markdown(
        f"""
        <div style="
            font-weight:600;
            font-size:22px;
            line-height:1.4;
            margin-top:10px;
            margin-bottom:10px;
        ">
            {truncate_text(main_video["title"], 80)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 선택 버튼 (Hero 영상)
    if st.button("이 영상 보기 🔎", key=f"main_{main_video['video_id']}"):
        st.session_state.selected_video_id = main_video["video_id"]
        st.session_state.summary = None
        st.session_state.timeline = []
        st.session_state.error = None
        st.rerun()

    # ======================================================
    # 5️⃣ 나머지 영상
    # ======================================================

    if len(videos) > 1:

        st.markdown("---")
        st.markdown("### 📺 그 외 추천 영상")

        cols = st.columns(len(videos) - 1)

        for idx, video in enumerate(videos[1:]):

            with cols[idx]:

                st.image(video["thumbnail_url"], width="stretch")

                st.markdown(
                    f"""
                    <div style="
                        font-weight:600;
                        font-size:16px;
                        line-height:1.4;
                        margin-bottom:10px;
                        display:-webkit-box;
                        -webkit-line-clamp:2;
                        -webkit-box-orient:vertical;
                        overflow:hidden;
                    ">
                        {truncate_text(video["title"], 60)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button("이 영상 보기 🔎", key=f"sub_{video['video_id']}"):
                    st.session_state.selected_video_id = video["video_id"]
                    st.session_state.summary = None
                    st.session_state.timeline = []
                    st.session_state.error = None
                    st.rerun()