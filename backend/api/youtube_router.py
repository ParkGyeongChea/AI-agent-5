# 
# YouTube 관련 API 라우터

from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
import asyncio #3.6 추가
from backend.schemas.youtube_schema import YouTubeInfo, YouTubeMetaData, YouTubeTimeLine, YouTubeFullDetail, YouTubeTranscribe
from backend.services import youtube_service, llm_service

router = APIRouter()

class RequestData(BaseModel):
    query: str


@router.post("/video/search/{query}", response_model=List[YouTubeInfo])
async def get_video_infos(query:str):
    return youtube_service.get_video_list(query=query)

@router.post("/video/info/metadata/{viedo_id}", response_model=YouTubeMetaData)
async def get_video_data(viedo_id:str):
    return youtube_service.get_video_metadata(video_id=viedo_id)

@router.post("/video/info/transcribe/{viedo_id}", response_model=YouTubeTranscribe)
async def get_transcrabe(viedo_id:str):
    return youtube_service.get_video_transcribe(viedo_id)

@router.post("/video/info/timeline/{viedo_id}", response_model=YouTubeTimeLine)
async def get_video_timeline(viedo_id:str):
    return youtube_service.get_video_timeline(viedo_id)

# @router.post("/video/info/full/{viedo_id}", response_model=YouTubeFullDetail)
# async def get_video_full_detail(viedo_id:str):
    
    
#     full_data = youtube_service.get_video_full_detail(viedo_id)
    
#     summary_data = await llm_service.summarize_transcript(
#         full_data.transcribe.transcript
#     )
    
#     full_data.summary = summary_data.get("summary")
#     full_data.timeline = summary_data.get("timeline")
    
    
#     return full_data


@router.post("/video/info/full/{viedo_id}", response_model=YouTubeFullDetail)
async def get_video_full_detail(viedo_id:str):

    full_data = youtube_service.get_video_full_detail(viedo_id)

    # 자막 가져오기
    transcript = full_data.transcribe.transcript

    
    
    
    #자막 없는 영상 gpt 호출하지 않는 코드 , 이 코드 적용하려면 아래 영상 요약 코드 주석 처리 필요.
    # if transcript:
    #     summary_data = await llm_service.summarize_transcript(transcript)
    # else:
    #     summary_data = {"summary": "", "timeline": []}


    # 영상 요약
    summary_data = await llm_service.summarize_transcript(transcript)

    full_data.summary = summary_data.get("summary")
    full_data.timeline = summary_data.get("timeline")

    return full_data



# @router.post("/recommend")
# def recommend(data: RequestData):

#     videos = youtube_service.get_video_list(query=data.query, count=3)

#     result = []

#     for video in videos:
#         metadata = youtube_service.get_video_metadata(video.video_id)

#         summary = llm_service.summarize_video(
#             metadata.title,
#             metadata.description
#         )

#         result.append({
#             "title": metadata.title,
#             "url": f"https://www.youtube.com/watch?v={metadata.video_id}",
#             "description": metadata.description,
#             "thumbnail": metadata.thumbnail_url,
#             "llm_output": summary
#         })

#     return {"videos": result}

#이 코드는 영상마다 GPT를 호출



@router.post("/recommend")
def recommend(data: RequestData):

    videos = youtube_service.get_video_list(query=data.query, count=3)

    metadatas = []

    for video in videos:
        metadatas.append({
            "title": video.title,
            "description": video.description,
            "video_id": video.video_id,
            "thumbnail": video.thumbnail_url
        })

    summary_results = llm_service.summarize_videos(metadatas)

    results = []

    for i, video in enumerate(metadatas):
        results.append({
            "title": video["title"],
            "url": f"https://www.youtube.com/watch?v={video['video_id']}",
            "description": video["description"],
            "thumbnail": video["thumbnail"],
            "llm_output": summary_results[i]
        })

    return {"videos": results}




@router.post("/recommend/full")
async def recommend_full(data: RequestData):

    videos = youtube_service.get_video_list(query=data.query, count=3)
    tasks = [] #비동기 작업 담을 빈 리스트 여기에 영상 3개를 넣고 한번에 실행

    for video in videos:
        video_id = video.video_id 
        tasks.append(get_video_full_detail(video_id))

    results = await asyncio.gather(*tasks)
    return {"videos": results}


@router.post("/test/video/{search}", response_model=List[YouTubeInfo])
async def test_video_search_list(search:str):
    yt_list = [
        {
            "video_id": "T6z-0dpXPvU",
            "title": "파이썬 무료 강의 100분 완성 (1분 파이썬 모음)",
            "url": "https://www.youtube.com/watch?v=T6z-0dpXPvU",
            "thumbnail_url": "https://img.youtube.com/vi/T6z-0dpXPvU/0.jpg"
        },
        {
            "video_id": "yytWGELNeOI",
            "title": "파이썬 무료 기초 강의 - 1강 파이썬이란 무엇인가?",
            "url": "https://www.youtube.com/watch?v=yytWGELNeOI",
            "thumbnail_url": "https://img.youtube.com/vi/yytWGELNeOI/0.jpg"
        },
        {
            "video_id": "kWiCuklohdY",
            "title": "파이썬 코딩 무료 강의 (기본편) - 6시간 뒤면 여러분도 개발자가 될 수 있어요 [나도코딩]",
            "url": "https://www.youtube.com/watch?v=kWiCuklohdY",
            "thumbnail_url": "https://img.youtube.com/vi/kWiCuklohdY/0.jpg"
        }
    ]
    
    return  [
        YouTubeInfo(
            video_id=info['video_id'],
            thumbnail_url=info['thumbnail_url'],
            title=info['title'],
            url=info['url'],
        )for info in yt_list
    ]

@router.post("/test/video/info/full/{video_id}", response_model=YouTubeFullDetail)
async def test_video_timeline(video_id:str):
    yt_list = [
        {
            "video_id": "T6z-0dpXPvU",
            "title": "파이썬 무료 강의 100분 완성 (1분 파이썬 모음)",
            "url": "https://www.youtube.com/watch?v=T6z-0dpXPvU",
            "thumbnail_url": "https://i.ytimg.com/vi/T6z-0dpXPvU/maxresdefault.jpg",
            "description": "#파이썬\n\n1분 파이썬 모음집입니다.\n비전공자도 이해할 수 있도록 실습 대신 이론 위주의 컨텐츠로 구성하여 100분 만에 빠르게 파이썬을 학습하실 수 있습니다. ^^\n\n\n【신규 강의 안내】\n✨ 챗GPT를 넘어서, 랭체인과 RAG로 만드는 AI 문서 Q&A 챗봇 강의\n👉 https://bit.ly/nadoRAG\n\n\n\n[목차]\n(0:00:00) 1.소개\n(0:01:11) 2.환경설정\n(0:02:22) 3.자료형\n(0:03:33) 4.변수\n(0:04:44) 5.변수 이름\n(0:05:55) 6.형 변환\n(0:07:31) 7.연산자\n(0:10:03) 8.불리안\n(0:11:21) 9.주석\n(0:12:47) 10.인덱스와 슬라이싱\n(0:14:57) 11.문자열 처리\n(0:16:36) 12.문자열 메소드 1\n(0:18:05) 13.문자열 메소드 2\n(0:19:44) 14.문자열 포맷\n(0:21:29) 15.탈출 문자\n(0:23:10) 16.리스트 1\n(0:24:37) 17.리스트 2\n(0:26:01) 18.튜플 1\n(0:27:24) 19.튜플 2\n(0:28:41) 20.세트 1\n(0:30:26) 21.세트 2\n(0:31:44) 22.딕셔너리 1\n(0:33:15) 23.딕셔너리 2\n(0:34:44) 24.자료형 비교\n(0:36:39) 25.자료형 변환\n(0:38:33) 26.if 조건문 1\n(0:40:50) 27.if 조건문 2\n(0:42:40) 28.if 중첩\n(0:45:12) 29.for 반복문\n(0:46:58) 30.range\n(0:48:29) 31.for 활용\n(0:49:58) 32.while\n(0:51:42) 33.break\n(0:53:11) 34.continue\n(0:54:24) 35.들여쓰기\n(0:55:34) 36.리스트 컴프리헨션\n(0:58:21) 37.함수\n(1:00:55) 38.전달값\n(1:02:34) 39.반환값\n(1:04:30) 40.기본값\n(1:05:57) 41.키워드값\n(1:07:26) 42.가변인자\n(1:09:19) 43.지역변수\n(1:10:28) 44.전역변수\n(1:11:49) 45.사용자입력\n(1:13:39) 46.파일입출력\n(1:15:46) 47.with\n(1:17:10) 48.클래스\n(1:19:21) 49.클래스 정의\n(1:21:17) 50.__init__\n(1:23:19) 51.멤버변수\n(1:24:14) 52.메소드\n(1:26:09) 53.self\n(1:27:59) 54.상속\n(1:30:07) 55.super\n(1:32:13) 56.다중상속\n(1:33:56) 57.메소드 오버라이딩\n(1:35:36) 58.pass\n(1:36:26) 59.예외처리\n(1:39:24) 60.에러\n(1:42:02) 61.모듈\n(1:44:33) 62.패키지\n\n\n보다 자세한 내용과 다양한 실습을 함께 하실 분은 6시간 분량의 '파이썬 기본편' 을 권해 드립니다.\n바로가기 : https://youtu.be/kWiCuklohdY\n\n\n✅ 나도코딩의 자바 기본편 강의\n👉 https://inf.run/BUS6\n\n\nDesigned by freepik, flaticon\n : https://www.freepik.com\n : https://www.flaticon.com",
            "channel_name": "나도코딩",
            "transcribe": {
                "transcript": []
            },
            "summary": "이 영상은 특정 주제에 대한 심층적인 분석을 제공합니다. 다양한 사례와 데이터를 통해 주제를 설명하며, 시청자에게 유용한 정보를 전달합니다. 또한, 전문가의 의견과 함께 실질적인 조언을 포함하고 있습니다. 마지막으로, 주제에 대한 결론과 향후 전망을 제시합니다.",
            "timeline": [
                {
                "time": "00:00",
                "summary": "영상 소개 및 주제 설명"
                },
                {
                "time": "05:00",
                "summary": "주제에 대한 사례 분석"
                },
                {
                "time": "10:00",
                "summary": "전문가 의견 및 결론 제시"
                }
            ]
        },
        {
            "video_id": "yytWGELNeOI",
            "title": "파이썬 무료 기초 강의 - 1강 파이썬이란 무엇인가?",
            "url": "https://www.youtube.com/watch?v=yytWGELNeOI",
            "thumbnail_url": "https://i.ytimg.com/vi_webp/yytWGELNeOI/maxresdefault.webp",
            "description": "점프 투 파이썬과 함께하는 파이썬 입문용 코딩 기초 강의 1강으로 프로그래밍을 전혀 모르는 왕초보도 누구나 쉽게 코딩을 배울 수 있도록 강의를 진행합니다.\n\n2022년 버전의 리뉴얼 강의가 업로드 되었습니다!\n▶https://youtu.be/KL1MIuBfWe0\n\n목차\n첫째마당. 파이썬 기본 문법 익히기\n01장 파이썬이란 무엇인가?\n00:00 인트로\n00:28 01-1 파이썬 시작하기\n01:45 01-2 파이썬의 특징\n05:33 01-3 파이썬으로 무엇을 할 수 있을까?\n08:45 01-4 파이썬 설치하기\n10:16 01-5 파이썬 둘러보기\n13:30 01-6 파이썬과 에디터 (Visual Stuido Code 설치)\n19:12 요약정리\n\n라이브 강의는 매주 일요일 저녁 8시에 진행합니다.\n\n조코딩의 파이썬 기초 강좌 (점프 투 파이썬) 재생목록 : https://www.youtube.com/playlist?list=PLU9-uwewPMe2AX9o9hFgv-nRvOcBdzvP5\n1강 라이브 풀버전 : https://youtu.be/1M9EOxQIT7k\n라이브 풀버전 재생목록 : https://www.youtube.com/playlist?list=PLU9-uwewPMe2L7dC2us_C3LLwDL9vHQIx\n\n책 구매하기 : https://coupa.ng/bDJBfK\n(위 링크는 쿠팡 파트너스와 연결된 링크로 구매에 따른 일정액의 수수료를 지급받을 수 있습니다.)\n\n#파이썬 #파이썬기초 #파이썬강의\n--\n이 영상은 이지스 퍼블리싱 출판사의 지원을 받아 제작되었습니다.",
            "channel_name": "조코딩 JoCoding",
            "transcribe": {
                "transcript": []
            },
            "summary": "이 영상은 주제에 대한 깊이 있는 분석과 다양한 사례를 통해 시청자에게 중요한 정보를 제공합니다. 각 섹션에서는 주제의 배경, 현재 상황, 그리고 미래 전망에 대해 설명합니다. 또한, 전문가의 의견과 통계 자료를 통해 신뢰성을 높이고 있습니다. 마지막으로, 시청자에게 실질적인 조언과 행동 지침을 제시합니다.",
            "timeline": [
                {
                "time": "00:00",
                "summary": "영상 소개 및 주제 설명"
                },
                {
                "time": "05:00",
                "summary": "주제의 배경과 역사적 맥락"
                },
                {
                "time": "10:00",
                "summary": "현재 상황과 전문가 의견"
                }
            ]
        },
        {
            "video_id": "kWiCuklohdY",
            "title": "파이썬 코딩 무료 강의 (기본편) - 6시간 뒤면 여러분도 개발자가 될 수 있어요 [나도코딩]",
            "url": "https://www.youtube.com/watch?v=kWiCuklohdY",
            "thumbnail_url": "https://i.ytimg.com/vi/kWiCuklohdY/maxresdefault.jpg",
            "description": "파이썬 무료 강의 (기본편)입니다.\n누구나 볼 수 있도록 쉽고 재미있게 제작하였습니다. ^^\n\n파이썬은 다양한 활용 분야가 있는 인기 최고의 프로그래밍 언어입니다.\n수많은 컴퓨터 교육 기관에서 가르치고 있으며 학생들도 배우고 있지요.\n여러분의 가치를 훨씬 높일 수 있는 필살기,\n지금 바로 시작하세요 !\n\n【신규 강의 안내】\n✨ 챗GPT를 넘어서, 랭체인과 RAG로 만드는 AI 문서 Q&A 챗봇 강의\n👉 https://bit.ly/nadoRAG\n\n\n✅ 파이썬 기본편 (6시간) 강의, 이제는 책으로 만나보세요 🙌\n👉 http://gilbut.co/c/23026846Ic\n\n\n✅ 오류정정 (2020.03.28 최종수정)\n9-7. 클래스 \"연산자 오버로딩\" 제목 및 설명이 잘못되어 정정합니다.\n해당 영상에 나오는 설명 중 \"연산자 오버로딩\"은 잘못된 워딩이며 \"메소드 오버라이딩\"이 올바른 표현입니다.\n\n9-9. 클래스 super (4:23:10) 내용 설명이 잘못되어 정정합니다.\nclass FlyableUnit(Flyable, Unit):\n def __init__(self):\n  super().__init__()\n위처럼 다중 상속 코드를 작성했을 때, super() 를 쓰면 순서상 맨 \"마지막\" 이 아닌, 맨 \"처음\" 클래스(예제에서는 Flyable) 에 대해서 __init__ 함수가 호출 됩니다.\n\n9-11. 스타크래프트 프로젝트 후반전 (4:40:32) 내용 설명이 잘못되어 정정합니다.\n5이상 20이하의 값을 얻기 위해서 randint(5, 20) 이나 randrange(5, 21) 로 작성해야 합니다.\n\n혼란을 드려 대단히 죄송합니다.\n\n\n✅ 활용편 커리큘럼\n기본편을 공부하신 분들을 위한 실전 활용편 강의입니다.\n활용편은 서로 연관성이 없으므로 원하시는 주제를 선택하셔서 들으시면 됩니다.\n\n1. 게임 개발 [완료] \n - 오락실에서 하던 Pang 게임\n - 바로가기 : https://youtu.be/Dkx8Pl6QKW0\n2. GUI 프로그래밍 [완료]\n - 영상에서 캡처한 이미지들을 하나로 합치는 프로그램\n - 바로가기 : https://youtu.be/bKPIcoou9N8\n3. 웹스크래핑 [완료]\n - 내가 원하는 뉴스를 매일 자동으로 긁어오는 프로그램\n - 바로가기 : https://youtu.be/yQ20jZwDjTE\n4. 업무자동화 [완료]\n - 엑셀, 인터넷, 데스크탑 등 컴퓨터에게 일을 시키는 스크립트\n - 바로가기 : https://youtu.be/exgO1LFl9x8\n5. 데이터 분석 및 시각화 [완료]\n - 빅데이터를 활용한 대한민국의 인구 문제 분석\n - 바로가기 : https://youtu.be/PjhlUzp_cU0\n6. 이미지 처리 [완료]\n - 이미지 / 영상에서 얼굴을 인식하여 얼굴 위에 재밌는 캐릭터 씌우기\n - 바로가기 : https://youtu.be/XK3eU9egll8\n7. 머신러닝 [완료]\n - 머신러닝을 이용하여 나만의 영화 추천 시스템 만들기\n - 바로가기 : https://youtu.be/TNcfJHajqJY\n8. 사물인터넷\n - 아두이노를 활용한 RC Car 제작\n\n\n✅ 목차\n(0:00) 0.Intro\n(0:38) 1-1.소개\n(02:22) 1-2.환경설정\n(07:26) 2-1.숫자 자료형\n(11:42) 2-2.문자열 자료형\n(13:08) 2-3.boolean 자료형\n(15:05) 2-4.변수\n(22:08) 2-5.주석\n(23:57) 2-6.퀴즈 #1\n(25:48) 3-1.연산자\n(33:23) 3-2.간단한수식\n(36:26) 3-3.숫자처리함수\n(38:59) 3-4.랜덤함수\n(44:11) 3-5.퀴즈 #2\n(46:57) 4-1.문자열\n(48:24) 4-2.슬라이싱\n(55:09) 4-3.문자열처리함수\n(1:00:56) 4-4.문자열포맷\n(1:09:17) 4-5.탈출문자\n(1:15:47) 4-6.퀴즈 #3\n(1:22:31) 5-1.리스트\n(1:31:35) 5-2.사전\n(1:40:46) 5-3.튜플\n(1:43:19) 5-4.세트\n(1:48:44) 5-5.자료구조의 변경\n(1:50:47) 5-6.퀴즈 #4\n(1:57:33) 6-1.if\n(2:05:08) 6-2.for\n(2:09:33) 6-3.while\n(2:14:59) 6-4.continue 와 break\n(2:19:11) 6-5.한 줄 for\n(2:22:51) 6-6.퀴즈 #5\n(2:28:36) 7-1.함수\n(2:30:09) 7-2.전달값과 반환값\n(2:37:50) 7-3.기본값\n(2:41:32) 7-4.키워드값\n(2:43:07) 7-5.가변인자\n(2:47:55) 7-6.지역변수와 전역변수\n(2:53:58) 7-7.퀴즈 #6\n(2:58:59) 8-1.표준입출력\n(3:10:12) 8-2.다양한 출력포맷\n(3:17:45) 8-3.파일입출력\n(3:26:27) 8-4.pickle\n(3:30:22) 8-5.with\n(3:33:33) 8-6.퀴즈 #7\n(3:38:08) 9-1.클래스\n(3:47:04) 9-2._init_\n(3:48:34) 9-3.멤버변수\n(3:53:07) 9-4.메소드\n(3:59:29) 9-5.상속\n(4:02:54) 9-6.다중상속\n(4:10:08) 9-7.메소드 오버라이딩\n(4:17:03) 9-8.pass\n(4:19:31) 9-9.super\n(4:23:50) 9-10.스타크래프트 프로젝트 전반전\n(4:33:47) 9-11.스타크래프트 프로젝트 후반전\n(4:44:42) 9-12.퀴즈 #8\n(4:50:13) 10-1.예외처리\n(4:58:15) 10-2.에러 발생시키기\n(5:01:06) 10-3.사용자 정의 예외처리\n(5:04:28) 10-4.finally\n(5:06:19) 10-5.퀴즈 #9\n(5:14:23) 11-1.모듈\n(5:24:10) 11-2.패키지\n(5:30:30) 11-3._all_\n(5:34:16) 11-4.모듈 직접 실행\n(5:37:00) 11-5.패키지, 모듈 위치\n(5:40:33) 11-6.pip install\n(5:46:04) 11-7.내장함수\n(5:50:38) 11-8.외장함수\n(5:58:49) 11-9.퀴즈 #10\n(6:01:08) 12.Outro\n\n\n✅ 나도코딩의 자바 기본편 강의\n👉 https://inf.run/BUS6\n\n\n\n\nDesigned by freepik\n : https://www.freepik.com",
            "channel_name": "나도코딩",
            "transcribe": {
                "transcript": []
            },
            "summary": "이 영상은 특정 주제에 대한 심층적인 분석을 제공합니다. 다양한 사례와 데이터를 통해 주제를 설명하며, 시청자에게 유용한 정보를 전달합니다. 또한, 전문가의 의견과 함께 실질적인 조언을 포함하고 있습니다. 마지막으로, 주제에 대한 결론과 향후 전망을 제시합니다.",
            "timeline": [
                {
                "time": "00:00",
                "summary": "영상 소개 및 주제 설명"
                },
                {
                "time": "05:00",
                "summary": "주제에 대한 사례 분석 및 데이터 제공"
                },
                {
                "time": "10:00",
                "summary": "전문가 의견 및 실질적인 조언 제시"
                }
            ]
        }
    ]
    
    info = next(
        (yt_info for yt_info in yt_list if video_id == yt_info['video_id']),
        None
    )
    return YouTubeFullDetail(
            video_id=info['video_id'],
            thumbnail_url=info['thumbnail_url'],
            title=info['title'],
            url=info['thumbnail_url'],
            channel_name=info['channel_name'],
            description=info['description'],
            summary=info['summary'],
            timeline=info['timeline'],
            transcribe=info['transcribe'],
        )