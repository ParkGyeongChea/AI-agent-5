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

@router.post("/video/info/transcribe/{video_id}", response_model=YouTubeTranscribe)
async def get_transcrabe(video_id:str):
    return youtube_service.get_video_transcribe(video_id)

@router.post("/video/info/timeline/{video_id}", response_model=YouTubeTimeLine)
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

@router.post("/video/info/transcribe/{video_id}", response_model=YouTubeTranscribe)
async def get_transcribe(video_id:str):
    return youtube_service.get_video_transcribe(video_id)

@router.post("/video/info/timeline/{video_id}", response_model=YouTubeTimeLine)
async def get_video_timeline(video_id:str):
    return youtube_service.get_video_timeline(video_id)



@router.post("/video/info/full/{video_id}", response_model=YouTubeFullDetail)
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

@router.post("/video/info/timeline-summary/{video_id}", response_model=YouTubeFullDetail)
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

@router.post("/video/service/quiz/{video_id}")
async def get_video_quiz(video_id:str, questions:int=5, difficulty="mid"): # Low | Mid | High
    """
    강의 영상에 맞는 퀴즈를 생성한다.  - LLM 모델 호출
    """
    
    transcripts = youtube_service.get_video_transcribe(video_id=video_id)
    result = llm_service.get_video_quiz(transcripts.get_full_transcript(), difficulty, questions)
    return result



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




