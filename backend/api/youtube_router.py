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
        [
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
    ]
    
    return  [
        YouTubeInfo(
            video_id=info['video_id'],
            thumbnail_url=info['thumbnail_url'],
            title=info['title'],
            url=info['url'],
            channel_name=info['channel_name'],
            duration=info['duration'],
        )for info in yt_list
    ]

@router.post("/test/video/info/full/{video_id}", response_model=YouTubeFullDetail)
async def test_video_timeline(video_id:str):
    yt_list = [
        {
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