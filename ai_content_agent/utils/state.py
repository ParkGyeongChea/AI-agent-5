"""
state.py (데이터 모델 레이어)

상태 모델 정의
상태 초기화
상태 구조 관리

streamlit은 버튼을 누를 때마다
스크립트를 처음부터 다시 실행한다

따라서 우리는 st.session_state를 사용해
데이터를 저장해야 한다
→ 파일은 다시 실행됨
→ 하지만 session_state는 메모리에 유지됨

이 파일은 앱에서 사용할
기본 상태를 초기화하는 역할을 한다

Streamlit Rerun 구조
1. 사용자가 버튼 클릭
2. 브라우저 → 서버에 이벤트 전송
3. Streamlit 서버가 app.py 파일을 처음부터 다시 실행
4. 화면을 다시 그려서 브라우저에 전송

즉, Streamlit은 "상태 기반 UI"가 아니라
"스크립트 순차 재실행 기반 UI"다

[사용자 행동]
    ↓
파일 rerun
    ↓
init_state 실행
    ↓
조건이 없으면 상태 초기화
    ↓
데이터 사라짐
"""

import streamlit as st

# app.py가 실행될 때마다 같이 실행된다
# AI 서비스의 전체 상태 모델
def init_state() :   # 안전한 기본 상태 보장 함수
    """
    이 함수는 앱이 처음 실행될 때
    필요한 기본 상태값을 세팅한다
    
    Streamlit은 rerun 구조라
    상태를 직접 관리하지 않으면 값이 사라진다
    """
    # -------------------------------------------------
    # 기본 상태 설계 (서비스 상태 설계도)
    
    # None	  아직 생성되지 않음
    # ""	  생성됐지만 비어 있음
    # []	  데이터 구조는 존재하지만 비어 있음
    # False   참/거짓 플래그
    
    # query	    문자열이니까 ""
    # videos	목록이니까 []
    # summary	아직 생성 안 됐으니까 None
    # loading	참/거짓이니까 False
    # -------------------------------------------------
    default_state = {
        "query" : "",                  # 사용자가 입력한 질문
        "videos" : [],                 # 추천된 영상 목록
        "selected_video_id" : None,    # 클릭한 영상 id
        "summary" : None,              # 영상 요약 내용
        "timeline" : [],               # 타임라인 정보
        "loading_recommend" : False,   # 추천 로딩 상태 (추천 API 기다리는 상태)
        "loading_summary" : False,     # 요약 로딩 상태 (요약 API 기다리는 상태)
        "error" : None                 # 에러 메시지
    }
    # -------------------------------------------------
    # 세션에 값이 없으면 기본값 세팅
    
    # 1. 기본 상태 목록을 순회
    # 2. 세션에 해당 키가 없을 경우에만
    # 3. 기본값을 넣는다
    
    # 이미 값이 있으면 유지 없으면 새로 생성
    # 이게 Rerun 구조에서 살아남는 방법
    # -------------------------------------------------
    for key, value in default_state.items() :
        if key not in st.session_state :    # → 기존 데이터를 보호하는 안전장치
            st.session_state[key] = value
            # session_state → 사용자 세션 동안 유지되는 메모리 공간