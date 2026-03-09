"""
video_list.py

추천된 영상 목록을 화면에 렌더링하는 컴포넌트

1. 각 영상에 "선택 버튼" 추가
2. 클릭시 selected_video_id 상태 저장
3. 기존 summary 초기화 (향후 확장 대비)
4. 상태 기반 UI 흐름 완성
5. 첫 번째 영상은 Hero 영역으로 크게 표시
6. 나머지 영상은 하단에 가로 배치
7. 클릭 시 selected_video_id 상태 변경

상태 기반 설계:
- UI는 session_state를 읽기만 한다.
- 상태 변경은 버튼 클릭 시에만 발생한다.
- 선택 상태(selected_video_id)는 최소 정보만 저장한다.
- summary는 선택 이후 별도 서비스 호출로 처리된다.

session_state.videos
    ↓
[0] → 메인 영상
[1:] → 썸네일 영역

📌 데이터 흐름

session_state.videos (리스트)
    ↓
videos[0] → 메인 영상
videos[1:] → 보조 영상 목록
    ↓
버튼 클릭
    ↓
selected_video_id 변경
    ↓
Streamlit 전체 rerun
    ↓
우측 패널 반응
"""

# ==========================================================
# 1️⃣ 모듈 import
# ==========================================================

import streamlit as st

# ==========================================================
# 2️⃣ 텍스트 길이 제한 함수 (UI 스타일 유지용)
# ==========================================================

def truncate_text(text: str, max_length: int):
    """
    텍스트가 max_length보다 길면
    뒤를 잘라내고 ...을 붙인다.

    UI 스타일은 그대로 유지하면서
    길이만 안전하게 제한하기 위함.
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# ==========================================================
# 2️⃣ 영상 목록 렌더링 함수
# ==========================================================

def render_video_list() :
    """
    추천 영상 목록 렌더링 함수
    영상 목록을 YouTube 스타일로 렌더링한다
    
    상태 기반 UI이기 때문에
    session_state를 직접 참조한다
    """
    
    # --------------------------------------------------
    # 2-1 추천 결과가 없으면 렌더링 중단
    # --------------------------------------------------
    # videos는 항상 리스트 타입이다.
    # 빈 리스트([])는 False로 평가된다.
    #
    # 이 조건이 없으면:
    # - videos가 빈 상태에서도 UI가 그려짐
    # - 인덱스 접근 시 에러 발생 가능
    # ------------------------------------------------------

    if not st.session_state.videos : 
        return
    
    # ------------------------------------------------------
    # 2-2 로컬 변수로 복사 (가독성 향상)
    # ------------------------------------------------------
    # 매번 st.session_state.videos를 쓰는 대신
    # 지역 변수로 저장하여 가독성을 높인다.
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
    # videos는 항상 리스트 타입이다.
    # None이 아닌 이유:
    # → 반복 가능 타입 보장
    # ======================================================
    
    main_video = videos[0]
    
    # ------------------------------------------------------
    # 이미지 영역
    #
    # 실제 서비스에서는:
    # video["thumbnail_url"] 같은 데이터가 들어온다.
    #
    # 지금은 Mock 환경이므로 placeholder 사용.
    #
    # use_column_width=True는
    # 컬럼 너비에 맞춰 자동 조정한다.
    # ------------------------------------------------------

    # 🔥 선택된 경우 영상 플레이어 표시
    if st.session_state.get("selected_video_id") == main_video["id"]:
        st.video(f"https://www.youtube.com/watch?v={main_video['video_id']}")
    else:
        thumbnail_url = f"https://img.youtube.com/vi/{main_video['video_id']}/hqdefault.jpg"
        # st.image(thumbnail_url, width="stretch")
        
    # ------------------------------------------------------
    # 영상 메타 정보 출력
    #
    # title, channel, duration은
    # recommend_mock에서 정의된 데이터 구조를 따른다.
    # ------------------------------------------------------
    
    # st.write(f"### {main_video['title']}")
    # st.write(f"👤 {main_video['channel']}")
    # st.write(f"⏱️ {main_video['duration']}")
        
    # # --------------------------------------------------
    # # 2-3 선택 버튼 추가 (메인 영역)
    # # --------------------------------------------------
    # # Streamlit은 동일한 버튼이 여러개 있으면 구분하지 못한다
    # # 그래서 key를 반드시 지정해야 한다
    # # video['id']를 key로 사용하면 각 버튼이 고유하게 식별된다
    # # --------------------------------------------------
    
    # if st.button("이 영상 학습하기 📖", key = f"select_{main_video['id']}") :
        
        # --------------------------------------------------
        # 2-4 상태 변경
        # --------------------------------------------------
        # 선택된 영상 ID를 session_state에 저장
        # 이 값이 바뀌면 rerun 이후
        # 우측 패널에서 이 값을 읽어 반응하게 된다
        # --------------------------------------------------

        # # 선택 상태 업데이트
        # st.session_state.selected_video_id = main_video["id"]

        # # --------------------------------------------------
        # # 향후 확장 대비:
        # # summary 및 timeline 초기화
        # # --------------------------------------------------
        
        # st.session_state.summary = None
        # st.session_state.timeline = []

        # # --------------------------------------------------
        # # 기존 에러 초기화
        # # --------------------------------------------------
        
        # st.session_state.error = None
        
        # st.rerun()

    # ======================================================
    # 3️⃣ 나머지 영상 (하단 썸네일 영역)
    # ======================================================

    # 영상이 2개 이상일 때만 렌더링
    if len(videos) > 1 :
        
        st.markdown("---")
        st.markdown("### 📺 그 외 추천 영상")
        
        # 2컬럼 가로 배치
        # 영상이 3개라면 → 2컬럼 생성
        # 이렇게 하면 가로 배치가 자동으로 된다.
        cols = st.columns(len(videos) - 1)
        
        # --------------------------------------------------
        # 나머지 영상 반복
        #
        # videos[1:]은
        # 첫 번째를 제외한 나머지 리스트이다.
        # --------------------------------------------------
        
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

                # ------------------------------------------
                # 그 다음 선택 상태 표시
                # ------------------------------------------
                
                # if st.session_state.get("selected_video_id") == video["id"]:
                #     st.success("🟢 선택됨")