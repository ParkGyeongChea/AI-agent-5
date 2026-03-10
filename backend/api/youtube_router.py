# 
# YouTube 관련 API 라우터

from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
import asyncio #3.6 추가
from schemas.youtube_schema import YouTubeInfo, YouTubeTimeLine, YouTubeFullDetail, YouTubeTranscribe
from services import youtube_service, llm_service

router = APIRouter()

class RequestData(BaseModel):
    query: str


@router.post("/video/search/{query}", response_model=List[YouTubeInfo])
async def get_video_infos(query:str):
    return youtube_service.get_video_list(query=query)

# @router.post("/video/info/metadata/{viedo_id}", response_model=YouTubeInfo)
# async def get_video_data(viedo_id:str):
#     return youtube_service.get_video_metadata(video_id=viedo_id)

@router.post("/video/info/transcribe/{viedo_id}", response_model=YouTubeTranscribe)
async def get_transcrabe(video_id:str):
    return youtube_service.get_video_transcribe(video_id)

@router.post("/video/info/timeline/{viedo_id}", response_model=YouTubeTimeLine)
async def get_video_timeline(video_id:str):
    return youtube_service.get_video_timeline(video_id)

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
async def get_video_full_detail(video_id:str):
    full_data = youtube_service.get_video_full_detail(video_id)

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

@router.post("/video/info/timelne-summary/{video_id}", response_model=YouTubeFullDetail)
async def get_video_timeline_summary(video_id:str):
    """
    유튜브 타임라인(챕터) 정보와 요약 정보를 리턴한다. - LLM 모델 호출    
    """
    
    full_data = youtube_service.get_video_full_detail(video_id)
    summary_data = llm_service.get_video_timeline_summary(full_data.get_full_transcript())
    full_data.summary = summary_data.get("summary")
    full_data.timeline = summary_data.get("timeline")
    return full_data

@router.post("/video/service/lecture-note/{video_id}")
async def get_video_lecture_note(video_id:str):
    """
    유튜브 학습을 위한 프리미엄 강의 자료 - LLM 모델 호출    
    """
    
    transcripts = youtube_service.get_video_transcribe(video_id=video_id)
    result = llm_service.get_video_quzi(transcripts.get_full_transcript())
    return result

@router.post("/video/service/quiz/{viedo_id}")
async def get_video_quiz(viedo_id:str, questions:int=5, difficulty="mid"): # Low | Mid | High
    """
    강의 영상에 맞는 퀴즈를 생성한다.  - LLM 모델 호출
    """
    
    transcripts = youtube_service.get_video_transcribe(video_id=viedo_id)
    result = llm_service.get_video_quiz(transcripts.get_full_transcript(), difficulty, questions)
    return result

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
                "video_id": "yytWGELNeOI",
                "title": "파이썬 무료 기초 강의 - 1강 파이썬이란 무엇인가?",
                "url": "https://www.youtube.com/watch?v=yytWGELNeOI",
                "thumbnail_url": "https://img.youtube.com/vi/yytWGELNeOI/0.jpg",
                "description": "점프 투 파이썬과 함께하는 파이썬 입문용 코딩 기초 강의 1강으로 프로그래밍을 전혀 모르는 왕초보도 누구나 쉽게 코딩을 배울 수 있도록 강의를 진행합니다.\n\n2022년 버전의 리뉴얼 강의가 업로드 되었습니다!\n▶https://youtu.be/KL1MIuBfWe0\n\n목차\n첫째마당. 파이썬 기본 문법 익히기\n01장 파이썬이란 무엇인가?\n00:00 인트로\n00:28 01-1 파이썬 시작하기\n01:45 01-2 파이썬의 특징\n05:33 01-3 파이썬으로 무엇을 할 수 있을까?\n08:45 01-4 파이썬 설치하기\n10:16 01-5 파이썬 둘러보기\n13:30 01-6 파이썬과 에디터 (Visual Stuido Code 설치)\n19:12 요약정리\n\n라이브 강의는 매주 일요일 저녁 8시에 진행합니다.\n\n조코딩의 파이썬 기초 강좌 (점프 투 파이썬) 재생목록 : https://www.youtube.com/playlist?list=PLU9-uwewPMe2AX9o9hFgv-nRvOcBdzvP5\n1강 라이브 풀버전 : https://youtu.be/1M9EOxQIT7k\n라이브 풀버전 재생목록 : https://www.youtube.com/playlist?list=PLU9-uwewPMe2L7dC2us_C3LLwDL9vHQIx\n\n책 구매하기 : https://coupa.ng/bDJBfK\n(위 링크는 쿠팡 파트너스와 연결된 링크로 구매에 따른 일정액의 수수료를 지급받을 수 있습니다.)\n\n#파이썬 #파이썬기초 #파이썬강의\n--\n이 영상은 이지스 퍼블리싱 출판사의 지원을 받아 제작되었습니다.",
                "channel_name": "조코딩 JoCoding",
                "duration": 1336
            },
            {
                "video_id": "x1VFfTz30VE",
                "title": "파이썬 당신이 지금 당장 배워야하는 이유 (파이썬 기초)",
                "url": "https://www.youtube.com/watch?v=x1VFfTz30VE",
                "thumbnail_url": "https://img.youtube.com/vi/x1VFfTz30VE/0.jpg",
                "description": "#파이썬기초 #코딩 #프로그래밍 \n\n파이썬 기초를 배우면 자동화, 웹 개발, 데이터 분석까지 모두 가능해집니다.\n파이썬 기초는 반복 업무를 줄이고 아이디어를 실제 프로그램으로 구현할 수 있게 해주고,\nGPT 시대에도 파이썬 기초는 AI를 다루는 핵심 언어이자 생존 스킬입니다.\n\n00:00 파이썬을 배우면 뭘 할 수 있을까?\n01:01 파이썬을 배우면 할 수 있는 것들\n03:18 지금 당장 파이썬기초를 배워야하는 이유\n04:38 파이썬기초를 배우는 가장 효과적인 방법",
                "channel_name": "원투코딩 OneTwoCoding",
                "duration": 336
            },
            {
                "video_id": "3R6vFdb7YI4",
                "title": "파이썬 왕초보 기초 강의 - 파이썬 프로그래밍의 기초, 자료형(1)",
                "url": "https://www.youtube.com/watch?v=3R6vFdb7YI4",
                "thumbnail_url": "https://img.youtube.com/vi/3R6vFdb7YI4/0.jpg",
                "description": "점프 투 파이썬과 함께하는 파이썬 입문용 코딩 기초 강의 2강으로 프로그래밍을 전혀 모르는 왕초보도 누구나 쉽게 코딩을 배울 수 있도록 강의를 진행합니다.\n\n2022년 버전의 리뉴얼 강의가 업로드 되었습니다!\n▶https://youtu.be/KL1MIuBfWe0\n\n(오류 수정)\n13:31 b = '12123425125' 에 대해 print(b[::-2]) 결과가 7531 인 것처럼 표시되는데 512311입니다.\n19:01 a = ','.join([\"a\",\"b\",\"c\"])에 대해 print(a) 결과가 a = ','.join([\"a\",\"b\",\"c\"]) 인 것처럼 표시되는데 a,b,c입니다.\n\n목차\n첫째마당. 파이썬 기본 문법 익히기\n02장 파이썬 프로그래밍의 기초, 자료형\n02-1 숫자형\n02-2 문자열 자료형\n02-3 리스트 자료형\n\n라이브 강의는 매주 일요일 저녁 8시에 진행합니다.\n\n조코딩의 파이썬 기초 강좌 (점프 투 파이썬) 재생목록 : https://www.youtube.com/playlist?list=PLU9-uwewPMe2AX9o9hFgv-nRvOcBdzvP5\n2강 라이브 풀버전 : https://youtu.be/1M9EOxQIT7k\n라이브 풀버전 재생목록 : https://www.youtube.com/playlist?list=PLU9-uwewPMe2L7dC2us_C3LLwDL9vHQIx\n\n책 구매하기 : https://coupa.ng/bDJBfK\n(위 링크는 쿠팡 파트너스와 연결된 링크로 구매에 따른 일정액의 수수료를 지급받을 수 있습니다.)\n\n#파이썬 #파이썬기초 #파이썬강의\n--\n이 영상은 이지스 퍼블리싱 출판사의 지원을 받아 제작되었습니다.",
                "channel_name": "조코딩 JoCoding",
                "duration": 1718
            }
        ]
    
    
    return  [
        YouTubeInfo(
            video_id=info['video_id'],
            thumbnail_url=info['thumbnail_url'],
            title=info['title'],
            url=info['url'],
            channel_name=info['channel_name'],
            duration=info['duration'],
            description=info['description'],
        ) for info in yt_list
    ]

@router.post("/test/video/info/full/{video_id}", response_model=YouTubeFullDetail)
async def test_video_timeline(video_id:str):
    yt_list = [
        {
            "video_id": "T6z-0dpXPvU",
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
            summary=info['summary'],
            timeline=info['timeline'],
            transcribe=info['transcribe'],
        )


@router.post("/test/video/service/lecture-note/{video_id}")
async def test_video_lecture_note(video_id:str):
    """
    유튜브 학습을 위한 프리미엄 강의 자료 - LLM 모델 호출    
    """
    
    
    result = {
        "lecture_overview": {
            "topic": "파이썬 프로그래밍 기초 자료형",
            "difficulty_level": "초급",
            "prerequisites": []
        },
        "learning_objectives": [
            "자료형의 개념을 이해하고, 다양한 자료형을 사용할 수 있다.",
            "변수의 개념을 이해하고, 변수를 활용하여 데이터를 저장하고 조작할 수 있다.",
            "숫자형과 문자열 자료형의 기본적인 연산을 수행할 수 있다.",
            "리스트와 같은 복합 자료형을 이해하고 활용할 수 있다."
        ],
        "key_terms": [
            {
            "term": "자료형",
            "definition": "데이터의 종류를 나타내며, 숫자, 문자열, 리스트 등 다양한 형태가 있다."
            },
            {
            "term": "변수",
            "definition": "데이터를 저장하는 공간으로, 특정 값을 담을 수 있는 이름이 붙은 상자이다."
            },
            {
            "term": "숫자형",
            "definition": "정수형(int)과 실수형(float)으로 나뉘며, 수학적 연산이 가능한 자료형이다."
            },
            {
            "term": "문자열",
            "definition": "문자들의 집합으로, 작은 따옴표(') 또는 큰 따옴표(\")로 감싸서 표현한다."
            },
            {
            "term": "리스트",
            "definition": "여러 개의 값을 순서대로 저장할 수 있는 자료형으로, 대괄호([])로 감싸서 표현한다."
            }
        ],
        "table_of_contents": [
            "1. 자료형의 개념",
            "2. 변수의 개념",
            "3. 숫자형 자료형",
            "4. 문자열 자료형",
            "5. 리스트 자료형",
            "6. 연습문제"
        ],
        "core_content": [
            {
            "section_title": "1. 자료형의 개념",
            "concept_explanation": "자료형은 데이터의 종류를 나타내며, 프로그래밍에서 데이터의 타입을 정의하는 중요한 요소입니다. 자료형을 이해하면 해당 언어의 절반을 이해한 것과 같습니다. 파이썬에서는 숫자형, 문자열, 리스트, 딕셔너리, 집합 등 다양한 자료형이 존재합니다.",
            "visual_summary": "| 자료형   | 설명                       |\n|----------|---------------------------|\n| 숫자형   | 정수(int), 실수(float)     |\n| 문자열   | 문자들의 집합(str)        |\n| 리스트    | 여러 값을 저장하는 구조    |\n| 딕셔너리 | 키-값 쌍으로 저장하는 구조 |\n| 집합     | 중복되지 않는 값의 집합   |",
            "code_examples": [
                {
                "title": "자료형 확인하기",
                "code": "a = 1\nprint(type(a))\n\nb = 'Hello'\nprint(type(b))",
                "line_by_line_explanation": "1. 변수 a에 정수 1을 할당합니다.\n2. type() 함수를 사용하여 a의 자료형을 출력합니다.\n3. 변수 b에 문자열 'Hello'를 할당합니다.\n4. type() 함수를 사용하여 b의 자료형을 출력합니다.",
                "expected_output": "<class 'int'>\n<class 'str'>"
                }
            ],
            "common_mistakes": [
                "숫자와 문자열을 혼동하여 연산할 때 오류가 발생할 수 있다. / 숫자형과 문자열형의 차이를 이해하지 못함 / 자료형을 명확히 구분하여 사용해야 한다."
            ],
            "deep_dive": "> 💡 자료형은 프로그래밍 언어의 기본적인 구성 요소로, 각 언어마다 지원하는 자료형이 다를 수 있습니다. 파이썬은 동적 타이핑 언어로, 변수의 자료형을 명시적으로 선언할 필요가 없습니다.",
            "real_world_usage": "자료형은 데이터베이스, 웹 개발, 데이터 분석 등 다양한 분야에서 데이터를 처리하는 데 필수적입니다."
            },
            {
            "section_title": "2. 변수의 개념",
            "concept_explanation": "변수는 데이터를 저장하는 공간으로, 특정 값을 담을 수 있는 이름이 붙은 상자입니다. 변수는 수학에서의 변수와는 다르게, 프로그래밍에서는 값을 저장하고 조작하는 데 사용됩니다.",
            "visual_summary": "| 변수 이름 | 설명                       |\n|-----------|---------------------------|\n| a         | 정수형 변수               |\n| b         | 문자열형 변수             |",
            "code_examples": [
                {
                "title": "변수 사용하기",
                "code": "a = 3\nb = a + 2\nprint(b)",
                "line_by_line_explanation": "1. 변수 a에 3을 할당합니다.\n2. 변수 b에 a의 값에 2를 더한 값을 할당합니다.\n3. b의 값을 출력합니다.",
                "expected_output": "5"
                }
            ],
            "common_mistakes": [
                "변수에 값을 할당할 때 '='의 의미를 혼동할 수 있다. / '='는 대입 연산자로, 수학의 등호와는 다르다."
            ],
            "deep_dive": "> 💡 변수는 메모리에서 데이터를 저장하는 공간으로, 변수의 이름을 통해 해당 데이터를 참조할 수 있습니다. 변수의 이름은 의미 있는 이름으로 설정하는 것이 좋습니다.",
            "real_world_usage": "변수는 모든 프로그래밍에서 데이터를 저장하고 조작하는 데 필수적입니다."
            },
            {
            "section_title": "3. 숫자형 자료형",
            "concept_explanation": "숫자형 자료형은 정수형(int)과 실수형(float)으로 나뉘며, 수학적 연산이 가능합니다. 파이썬에서는 다양한 숫자형을 지원하며, 기본적인 사칙연산을 수행할 수 있습니다.",
            "visual_summary": "| 숫자형   | 설명                       |\n|----------|---------------------------|\n| 정수형   | 정수 값을 저장하는 자료형 |\n| 실수형   | 소수점을 포함한 값을 저장하는 자료형 |",
            "code_examples": [
                {
                "title": "숫자형 연산",
                "code": "a = 4\nb = 2\nprint(a + b)\nprint(a - b)\nprint(a * b)\nprint(a / b)",
                "line_by_line_explanation": "1. 변수 a에 4를 할당합니다.\n2. 변수 b에 2를 할당합니다.\n3. a와 b의 합을 출력합니다.\n4. a에서 b를 뺀 값을 출력합니다.\n5. a와 b의 곱을 출력합니다.\n6. a를 b로 나눈 값을 출력합니다.",
                "expected_output": "6\n2\n8\n2.0"
                }
            ],
            "common_mistakes": [
                "정수형과 실수형의 연산 결과를 혼동할 수 있다. / 정수형과 실수형의 연산 시 결과가 실수형으로 나오는 것을 이해해야 한다."
            ],
            "deep_dive": "> 💡 파이썬에서는 숫자형 자료형을 사용하여 다양한 수학적 계산을 수행할 수 있습니다. 또한, 숫자형 자료형은 메모리에서 효율적으로 처리됩니다.",
            "real_world_usage": "숫자형 자료형은 데이터 분석, 과학적 계산, 게임 개발 등 다양한 분야에서 사용됩니다."
            },
            {
            "section_title": "4. 문자열 자료형",
            "concept_explanation": "문자열 자료형은 문자들의 집합으로, 작은 따옴표(') 또는 큰 따옴표(\")로 감싸서 표현합니다. 문자열은 다양한 방법으로 조작할 수 있으며, 문자열 간의 연결, 반복, 인덱싱 등이 가능합니다.",
            "visual_summary": "| 문자열   | 설명                       |\n|----------|---------------------------|\n| 'Hello'  | 작은 따옴표로 감싼 문자열 |\n| \"World\" | 큰 따옴표로 감싼 문자열  |",
            "code_examples": [
                {
                "title": "문자열 조작",
                "code": "a = 'Hello'\nb = 'World'\nprint(a + ' ' + b)\nprint(a * 3)",
                "line_by_line_explanation": "1. 변수 a에 문자열 'Hello'를 할당합니다.\n2. 변수 b에 문자열 'World'를 할당합니다.\n3. a와 b를 연결하여 출력합니다.\n4. a를 3번 반복하여 출력합니다.",
                "expected_output": "Hello World\nHelloHelloHello"
                }
            ],
            "common_mistakes": [
                "문자열을 연결할 때 '+' 연산자를 사용하는 것을 잊을 수 있다. / 문자열과 숫자를 직접 연결하려고 할 때 오류가 발생할 수 있다."
            ],
            "deep_dive": "> 💡 문자열은 프로그래밍에서 가장 많이 사용되는 자료형 중 하나로, 사용자와의 상호작용, 데이터 출력 등에 필수적입니다.",
            "real_world_usage": "문자열은 웹 개발, 데이터 처리, 사용자 인터페이스 등 다양한 분야에서 사용됩니다."
            },
            {
            "section_title": "5. 리스트 자료형",
            "concept_explanation": "리스트는 여러 개의 값을 순서대로 저장할 수 있는 자료형으로, 대괄호([])로 감싸서 표현합니다. 리스트는 다양한 자료형을 혼합하여 저장할 수 있으며, 인덱싱과 슬라이싱을 통해 요소에 접근할 수 있습니다.",
            "visual_summary": "| 리스트    | 설명                       |\n|----------|---------------------------|\n| [1, 2, 3] | 정수형 리스트             |\n| ['a', 'b'] | 문자열 리스트             |",
            "code_examples": [
                {
                "title": "리스트 사용하기",
                "code": "my_list = [1, 2, 3]\nprint(my_list[0])\nmy_list.append(4)\nprint(my_list)",
                "line_by_line_explanation": "1. my_list라는 리스트에 정수 1, 2, 3을 저장합니다.\n2. my_list의 첫 번째 요소를 출력합니다.\n3. append() 메서드를 사용하여 4를 리스트에 추가합니다.\n4. 리스트의 전체 내용을 출력합니다.",
                "expected_output": "1\n[1, 2, 3, 4]"
                }
            ],
            "common_mistakes": [
                "리스트의 인덱스는 0부터 시작한다는 것을 잊을 수 있다. / 리스트에 요소를 추가할 때 append() 메서드를 사용해야 한다는 것을 잊을 수 있다."
            ],
            "deep_dive": "> 💡 리스트는 파이썬에서 가장 유용한 자료형 중 하나로, 데이터를 효율적으로 저장하고 조작할 수 있는 기능을 제공합니다.",
            "real_world_usage": "리스트는 데이터베이스, 웹 애플리케이션, 데이터 분석 등 다양한 분야에서 사용됩니다."
            },
            {
            "section_title": "6. 연습문제",
            "concept_explanation": "이 섹션에서는 배운 내용을 바탕으로 연습문제를 통해 이해도를 높입니다.",
            "visual_summary": "",
            "code_examples": [],
            "common_mistakes": [],
            "deep_dive": "",
            "real_world_usage": ""
            }
        ],
        "hands_on_practice": [
            {
            "exercise_title": "자료형과 변수 연습",
            "difficulty": "easy",
            "problem": "변수 a에 10을 할당하고, 변수 b에 a의 값에 5를 더한 값을 할당한 후, b의 값을 출력하시오.",
            "hint": "변수에 값을 할당할 때 '=' 연산자를 사용하세요.",
            "solution": "a = 10\nb = a + 5\nprint(b)",
            "solution_explanation": "변수 a에 10을 할당하고, 변수 b에 a의 값에 5를 더한 값을 할당한 후, b의 값을 출력합니다."
            },
            {
            "exercise_title": "숫자형 연산 연습",
            "difficulty": "medium",
            "problem": "변수 x에 15, y에 4를 할당한 후, x를 y로 나눈 몫과 나머지를 출력하시오.",
            "hint": "몫은 '//' 연산자를 사용하고, 나머지는 '%' 연산자를 사용하세요.",
            "solution": "x = 15\ny = 4\nprint(x // y)\nprint(x % y)",
            "solution_explanation": "변수 x에 15, y에 4를 할당한 후, x를 y로 나눈 몫과 나머지를 각각 출력합니다."
            },
            {
            "exercise_title": "문자열 조작 연습",
            "difficulty": "medium",
            "problem": "변수 greeting에 'Hello'를 할당하고, greeting을 3번 반복하여 출력하시오.",
            "hint": "문자열을 반복할 때는 '*' 연산자를 사용하세요.",
            "solution": "greeting = 'Hello'\nprint(greeting * 3)",
            "solution_explanation": "변수 greeting에 'Hello'를 할당하고, 이를 3번 반복하여 출력합니다."
            },
            {
            "exercise_title": "리스트 사용 연습",
            "difficulty": "hard",
            "problem": "리스트 fruits에 'apple', 'banana', 'cherry'를 추가한 후, 두 번째 요소를 출력하시오.",
            "hint": "리스트에 요소를 추가할 때는 append() 메서드를 사용하세요.",
            "solution": "fruits = ['apple', 'banana']\nfruits.append('cherry')\nprint(fruits[1])",
            "solution_explanation": "리스트 fruits에 'apple'과 'banana'를 추가한 후, 'cherry'를 append() 메서드를 사용하여 추가하고, 두 번째 요소를 출력합니다."
            }
        ],
        "core_faq": [
            {
            "question": "자료형이란 무엇인가요?",
            "answer": "자료형은 데이터의 종류를 나타내며, 프로그래밍에서 데이터의 타입을 정의하는 중요한 요소입니다."
            },
            {
            "question": "변수는 무엇인가요?",
            "answer": "변수는 데이터를 저장하는 공간으로, 특정 값을 담을 수 있는 이름이 붙은 상자입니다."
            },
            {
            "question": "리스트는 어떻게 사용하나요?",
            "answer": "리스트는 여러 개의 값을 순서대로 저장할 수 있는 자료형으로, 대괄호([])로 감싸서 표현합니다."
            }
        ],
        "further_study": [
            "파이썬 공식 문서에서 자료형에 대한 자세한 내용을 확인하세요.",
            "자료형과 관련된 다양한 연습문제를 풀어보세요.",
            "다양한 프로그래밍 언어에서의 자료형 비교를 통해 이해도를 높이세요."
        ]
    }
    return result

@router.post("/test/video/service/quiz/{viedo_id}")
async def test_video_quiz(
    viedo_id:str, 
    questions:int=5,    # 문항수(+ 도전문제)
    difficulty="mid"):  # Low | Mid | High
    
    """
    강의 영상에 맞는 퀴즈를 생성한다.  - LLM 모델 호출
    """
    result = {
        "metadata": {
            "created_at": "2026-03-10 15:15:13",
            "difficulty": "Mid"
        },
        "questions": [
            {
            "question": "파이썬에서 자료형의 중요성을 설명하시오. 자료형이 무엇인지, 그리고 숫자형과 문자열형의 차이점을 예를 들어 설명하시오.",
            "options": [
                "자료형은 데이터의 형식을 정의하며, 숫자형은 수치 데이터를, 문자열형은 문자 데이터를 저장한다.",
                "자료형은 데이터의 형식을 정의하며, 숫자형은 문자 데이터를, 문자열형은 수치 데이터를 저장한다.",
                "자료형은 데이터의 형식을 정의하지 않으며, 모든 데이터는 동일한 형식으로 저장된다.",
                "자료형은 데이터의 형식을 정의하며, 숫자형과 문자열형은 동일한 방식으로 데이터를 저장한다."
            ],
            "answer": "자료형은 데이터의 형식을 정의하며, 숫자형은 수치 데이터를, 문자열형은 문자 데이터를 저장한다."
            },
            {
            "question": "다음 코드의 출력 결과는 무엇인가? \n```python\na = 5\nb = '5'\nprint(a + b)\n```",
            "options": [
                "10",
                "55",
                "TypeError",
                "5"
            ],
            "answer": "TypeError"
            },
            {
            "question": "다음 코드의 결과로 올바른 것은 무엇인가? \n```python\nx = 'Hello'\ny = 'World'\nresult = x + ' ' + y\nprint(result)\n```",
            "options": [
                "HelloWorld",
                "Hello World",
                "Hello World!",
                "Hello+World"
            ],
            "answer": "Hello World"
            }
        ],
        "challenge": [
            {
            "question": "다음 조건을 만족하는 파이썬 함수를 작성하시오. \n- 입력: 문자열 (예: 'apple,banana,cherry') \n- 출력: 리스트 (예: ['apple', 'banana', 'cherry']) \n- 문자열을 ','를 기준으로 나누어 리스트로 반환해야 한다.",
            "answer": "```python\ndef split_string(input_string):\n    return input_string.split(',')\n\n# 예시 사용\nresult = split_string('apple,banana,cherry')\nprint(result)  # ['apple', 'banana', 'cherry']\n```"
            }
        ]
    }
    return result