
# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st

# ==========================================================
# 2️⃣ 텍스트 길이 제한 함수 (UI 스타일 유지용)
# ==========================================================

def truncate_text(text: str, max_length: int):

    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# ==========================================================
# 2️⃣ 영상 목록 렌더링 함수
# ==========================================================

def render_video_list() :

    # --------------------------------------------------
    # 2-1 추천 결과가 없으면 렌더링 중단
    # --------------------------------------------------

    if not st.session_state.videos : 
        return
    
    # ------------------------------------------------------
    # 2-2 로컬 변수로 복사 (가독성 향상)
    # ------------------------------------------------------
    
    videos = st.session_state.videos
    selected_id = st.session_state.get("selected_video_id")

    # 선택된 영상을 맨 앞으로 정렬
    if selected_id:
        videos = sorted(
            videos,
            key=lambda v: v["id"] != selected_id
        )
    
    search_query = st.session_state.get("search_query")
    
    st.markdown("---")

    if search_query:
        st.subheader(f"{search_query} 관련 학습 영상 🎬")
    else:
        st.subheader("추천 영상 목록 🎬")

    # ======================================================
    # 3️⃣ 첫 번째 영상 (Hero 영역)
    # ======================================================

    main_video = videos[0]
    
    # 🔥 선택된 경우 영상 플레이어 표시
    if st.session_state.get("selected_video_id") == main_video["id"]:
        st.video(f"https://www.youtube.com/watch?v={main_video['video_id']}")
    else:
        thumbnail_url = f"https://img.youtube.com/vi/{main_video['video_id']}/hqdefault.jpg"
        
    # ======================================================
    # 3️⃣ 나머지 영상 (하단 썸네일 영역)
    # ======================================================

    # 영상이 2개 이상일 때만 렌더링
    if len(videos) > 1 :
        
        st.markdown("---")
        st.markdown("### 📺 그 외 추천 영상")
        
        cols = st.columns(len(videos) - 1)
        
        for idx, video in enumerate(videos[1:]) :
            
            # 각 컬럼 안에 렌더링
            with cols[idx] :
                
                thumbnail_url = f"https://img.youtube.com/vi/{video['video_id']}/hqdefault.jpg"
                st.image(thumbnail_url, width="stretch")

                # -------------------------------
                # 🎯 텍스트 길이 제한 적용
                # -------------------------------

                title = truncate_text(video["title"], 60)
                channel = truncate_text(video["channel"], 40)

                # 기존 스타일 유지
                st.markdown(
                    f"""
                    <div style="
                        font-weight:600;
                        font-size:18px;
                        line-height:1.4;
                        margin-bottom:15px;
                        display:-webkit-box;
                        -webkit-line-clamp:2;
                        -webkit-box-orient:vertical;
                        overflow:hidden;
                    ">
                        {video['title']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write(f"👤 {channel}")
                st.write(f"⏱️ {video['duration']}")
                    
                # ------------------------------------------
                # 보조 영상 선택 버튼
                # ------------------------------------------
                
                if st.button("이 영상 보기 🔎", key=f"sub_{video['id']}") :
                    st.session_state.selected_video_id = video["id"]
                    st.session_state.summary = None
                    st.session_state.timeline = []
                    st.session_state.error = None
                    
                    st.rerun()    # 🔥 안정성 위해 유지