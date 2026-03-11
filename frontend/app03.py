import os
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ----------------------------
# Session State init
# ----------------------------
if "videos" not in st.session_state:
    st.session_state.videos = []

if "selected" not in st.session_state:
    st.session_state.selected = None

if "detail_cache" not in st.session_state:
    st.session_state.detail_cache = {}

if "quiz_cache" not in st.session_state:
    st.session_state.quiz_cache = {}

if "start_sec" not in st.session_state:
    st.session_state.start_sec = 0

if "autoplay_once" not in st.session_state:
    st.session_state.autoplay_once = False
    
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}  
    
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = {} 


st.set_page_config(layout="wide")
st.title("영상 추천 AI Agent")


# ----------------------------
# Helpers
# ----------------------------

def fmt_mmss(sec: int) -> str:
    sec = int(sec or 0)
    m = sec // 60
    s = sec % 60
    return f"{m}:{s:02d}"


def ellipsis(text: str, max_chars: int = 40) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def parse_time_to_seconds(time_str: str) -> int:

    if not time_str:
        return 0

    parts = time_str.strip().split(":")

    try:
        nums = [int(p) for p in parts]
    except Exception:
        return 0

    if len(nums) == 2:
        mm, ss = nums
        return mm * 60 + ss

    if len(nums) == 3:
        hh, mm, ss = nums
        return hh * 3600 + mm * 60 + ss

    return 0


def fetch_quiz(video_id: str, questions: int = 5, difficulty: str = "mid"):

    try:
        r = requests.post(
            f"{BACKEND_URL}/test/video/service/quiz/{video_id}",
            params={
                "questions": questions,
                "difficulty": difficulty
            },
            timeout=120
        )

        if r.status_code == 200:
            return r.json()

        return None

    except Exception:
        return None


# ----------------------------
# Top bar
# ----------------------------

with st.form("search_form", clear_on_submit=False):

    top1, top2 = st.columns([0.78, 0.22], vertical_alignment="bottom")

    with top1:
        keyword = st.text_input(
            "주제/키워드",
            placeholder="예: 파이썬 기초, langgraph agent 설계",
            label_visibility="collapsed",
            key="keyword_input",
        )

    with top2:
        fetch_btn = st.form_submit_button("관련 영상 3개 가져오기", use_container_width=True)


if fetch_btn:

    if not keyword.strip():
        st.warning("키워드를 입력하세요.")

    else:

        encoded_keyword = quote(keyword.strip())

        with st.spinner("추천 영상 가져오는 중..."):

            r = requests.post(
                f"{BACKEND_URL}/test/video/{encoded_keyword}",
                timeout=30,
            )

        if r.status_code != 200:
            st.error(r.text)

        else:

            videos = r.json() if isinstance(r.json(), list) else []

            normalized_videos = []

            for v in videos:

                video_id = v.get("video_id")

                if not video_id:
                    continue

                normalized_videos.append({
                    "video_id": video_id,
                    "title": v.get("title", ""),
                    "thumbnail": v.get("thumbnail_url", ""),
                    "url": v.get("url", ""),
                    "channel_name": v.get("channel_name", ""),
                })

            st.session_state.videos = normalized_videos

            st.session_state.selected = normalized_videos[0]["video_id"] if normalized_videos else None

            st.session_state.start_sec = 0

            st.session_state.autoplay_once = False

            if normalized_videos:

                first_vid = normalized_videos[0]["video_id"]

                if first_vid not in st.session_state.detail_cache:

                    with st.spinner("첫 번째 영상 요약 생성 중..."):

                        try:

                            sr = requests.post(
                                f"{BACKEND_URL}/test/video/info/full/{first_vid}",
                                timeout=120
                            )

                            if sr.status_code == 200:
                                st.session_state.detail_cache[first_vid] = sr.json()

                        except Exception:
                            pass

            st.rerun()


left, right = st.columns([0.60, 0.40], gap="large")


# ----------------------------
# Left
# ----------------------------

with left:

    st.subheader("Video")

    if not st.session_state.selected:

        st.info("키워드를 입력하고 추천을 받아오세요.")

    else:

        vid = st.session_state.selected
        start = int(st.session_state.start_sec)

        autoplay = "1" if st.session_state.autoplay_once else "0"

        if st.session_state.autoplay_once:
            st.session_state.autoplay_once = False

        src = f"https://www.youtube.com/embed/{vid}?start={start}&autoplay={autoplay}&mute=1"

        st.components.v1.html(
            f"""
            <iframe
                width="100%"
                height="560"
                src="{src}"
                frameborder="0"
                allow="autoplay; encrypted-media; picture-in-picture"
                allowfullscreen
            ></iframe>
            """,
            height=580
        )

        st.markdown("### Recommend List")

        for v in st.session_state.videos:

            c1, c2 = st.columns([0.25, 0.75])

            with c1:

                if v.get("thumbnail"):
                    st.image(v["thumbnail"], use_container_width=True)

            with c2:

                title = v.get("title") or v["video_id"]

                title_btn = ellipsis(title, 50)

                channel_name = (v.get("channel_name") or "").strip()

                if st.button(title_btn, key=f"sel_{v['video_id']}"):

                    st.session_state.selected = v["video_id"]

                    st.session_state.start_sec = 0

                    st.session_state.autoplay_once = False

                    st.rerun()

                if channel_name:

                    st.markdown(
                        f"""
                        <div style="margin-top:-6px; margin-bottom:6px; font-size:0.95rem; color: rgba(255,255,255,0.85);">
                            채널명 : {channel_name}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if v.get("url"):
                    st.markdown(f"[YouTube에서 열기]({v['url']})")

        # ----------------------------
        # Quiz
        # ----------------------------
        st.markdown("#### Quiz")

        # 현재 영상 기준 상태 초기화
        if vid not in st.session_state.quiz_answers:
            st.session_state.quiz_answers[vid] = {}

        if vid not in st.session_state.quiz_submitted:
            st.session_state.quiz_submitted[vid] = False

        # 퀴즈 자동 로드
        if vid not in st.session_state.quiz_cache:
            with st.spinner("퀴즈 생성 중..."):
                quiz_data = fetch_quiz(vid)
                if quiz_data:
                    st.session_state.quiz_cache[vid] = quiz_data

        quiz_data = st.session_state.quiz_cache.get(vid)

        if not quiz_data:
            st.caption("퀴즈 없음")

        else:
            questions = quiz_data.get("questions", [])
            challenge = quiz_data.get("challenge", [])

            if questions:
                st.caption("객관식 퀴즈를 풀고 채점 버튼을 눌러보세요.")

                for i, q in enumerate(questions, start=1):
                    q_key = f"{vid}_q_{i}"
                    question_text = q.get("question", "")
                    options = q.get("options", [])

                    with st.expander(f"Q{i}. {ellipsis(question_text, 100)}", expanded=(i == 1)):
                        st.write(question_text)

                        if options:
                            selected = st.radio(
                                "보기 선택",
                                options,
                                index=None,
                                key=q_key,
                                label_visibility="collapsed",
                            )

                            # 선택값 저장
                            if selected is not None:
                                st.session_state.quiz_answers[vid][i] = selected

                        # 채점 이후에만 정답/결과 표시
                        if st.session_state.quiz_submitted[vid]:
                            correct_answer = q.get("answer", "")
                            user_answer = st.session_state.quiz_answers[vid].get(i)

                            if user_answer == correct_answer:
                                st.success("정답입니다.")
                            else:
                                st.error("오답입니다.")

                            with st.expander("정답 보기", expanded=False):
                                st.write(correct_answer)

                # ----------------------------
                # 채점 / 다시풀기
                # ----------------------------
                c1, c2 = st.columns(2)

                with c1:
                    if st.button("채점하기", key=f"grade_{vid}", use_container_width=True):
                        st.session_state.quiz_submitted[vid] = True
                        st.rerun()

                with c2:
                    if st.button("다시 풀기", key=f"retry_{vid}", use_container_width=True):
                        st.session_state.quiz_answers[vid] = {}
                        st.session_state.quiz_submitted[vid] = False

                        # radio 위젯 상태도 초기화
                        for i in range(1, len(questions) + 1):
                            q_key = f"{vid}_q_{i}"
                            if q_key in st.session_state:
                                del st.session_state[q_key]

                        st.rerun()

                # ----------------------------
                # 점수 표시
                # ----------------------------
                if st.session_state.quiz_submitted[vid]:
                    score = 0
                    total = len(questions)

                    for i, q in enumerate(questions, start=1):
                        correct_answer = q.get("answer", "")
                        user_answer = st.session_state.quiz_answers[vid].get(i)

                        if user_answer == correct_answer:
                            score += 1

                    st.markdown(f"**점수: {score} / {total}**")

            # ----------------------------
            # Challenge
            # ----------------------------
            if challenge:
                st.markdown("##### Challenge")

                for i, q in enumerate(challenge, start=1):
                    with st.expander(f"도전문제 {i}"):

                        st.write(q.get("question", ""))

                        with st.expander("정답 보기"):
                            ans = q.get("answer", "")

                            # ```python 코드블록 제거 후 코드만 보여주기
                            if "```python" in ans:
                                cleaned = ans.replace("```python", "").replace("```", "").strip()
                                st.code(cleaned, language="python")
                            else:
                                st.write(ans)
# ----------------------------
# Right
# ----------------------------

with right:

    st.subheader("Summary / Timeline")

    vid = st.session_state.selected

    if not vid:
        st.info("왼쪽에서 영상을 선택하세요.")
        st.stop()

    if vid not in st.session_state.detail_cache:

        with st.spinner("요약 생성 중..."):

            r = requests.post(
                f"{BACKEND_URL}/test/video/info/full/{vid}",
                timeout=120
            )

        if r.status_code != 200:

            st.error("요약 실패")

            st.stop()

        st.session_state.detail_cache[vid] = r.json()

    data = st.session_state.detail_cache[vid]

    st.markdown("#### Summary")

    summary_text = data.get("summary", "")

    if summary_text:
        st.write(summary_text)

    else:
        st.caption("요약 없음")

    description = data.get("description", "")

    if description:

        with st.expander("Description", expanded=True):
            st.write(description)

    st.markdown("#### Timeline")

    timeline = data.get("timeline", [])

    if not timeline:
        st.caption("타임라인 없음")

    else:

        for i, item in enumerate(timeline):

            time_label = item.get("time", "00:00")

            start_s = parse_time_to_seconds(time_label)

            with st.expander(time_label, expanded=(i == 0)):

                st.write(item.get("summary", ""))

                if st.button(f"▶ {time_label}부터 재생", key=f"play_{vid}_{i}"):

                    st.session_state.start_sec = start_s

                    st.session_state.autoplay_once = True

                    st.rerun()

