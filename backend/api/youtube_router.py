# 
# YouTube 관련 API 라우터

# - 클라이언트(frontend) 요청을 받는 경로 정의
# - 요청(Request) → 서비스 호출 → 응답(Response) 반환

# ※ 여기에는 복잡한 로직을 작성하지 않는다.
# ※ 실제 처리 로직은 services/에서 호출한다.
# 


from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

from schemas.youtube_schema import YouTubeInfo, YouTubeMetaData, YouTubeTimeLineTranscribe, YouTubeChapters, YouTubeFullDetail
from services import youtube_service, llm_service

router = APIRouter()

class RequestData(BaseModel):
    query: str


@router.post("/video/search/{query}", response_model=List[YouTubeInfo])
async def get_video_infos(query:str):
    return youtube_service.get_video_list(query=query)

@router.post("/video/info/metadata/{viedo_id}", response_model=YouTubeMetaData)
async def get_video_data(viedo_id:str):
    return youtube_service.get_video_metadata(video_id=viedo_id)

@router.post("/video/info/transcribe/{viedo_id}", response_model=YouTubeTimeLineTranscribe)
async def get_transcrabe(viedo_id:str):
    return youtube_service.get_video_transcribe(viedo_id)

@router.post("/video/info/chapter/{viedo_id}", response_model=YouTubeChapters)
async def get_video_chapter(viedo_id:str):
    return youtube_service.get_video_chapter(viedo_id)

@router.post("/video/info/full/{viedo_id}", response_model=YouTubeFullDetail)
async def get_video_full_detail(viedo_id:str):
    
    full_data = youtube_service.get_video_full_detail(viedo_id)
    
    # 챕터 정보가 없으면 LLM 챕터 생성
    if not full_data.chapters.data:
        data = llm_service.chapter_split(full_data.get_full_transcript())       
        full_data.chapters = data
         
    #영상 요약 + 타임라인 생성
    summary_data = llm_service.summarize_transcript(
        full_data.get_full_transcript()
    )
    
    full_data.summary = summary_data.get("summary")
    full_data.timeline = summary_data.get("timeline")
    
    
    return full_data

@router.post("/recommend")
def recommend(data: RequestData):

    videos = youtube_service.get_video_list(query=data.query, count=3)

    result = []

    for video in videos:
        metadata = youtube_service.get_video_metadata(video.video_id)

        summary = llm_service.summarize_video(
            metadata.title,
            metadata.description
        )

        result.append({
            "title": metadata.title,
            "url": f"https://www.youtube.com/watch?v={metadata.video_id}",
            "description": metadata.description,
            "thumbnail": metadata.thumbnail_url,
            "llm_output": summary
        })

    return {"videos": result}

@router.post("/recommend/full")
async def recommend_full(data: RequestData):

    videos = youtube_service.get_video_list(query=data.query, count=3)

    results = []

    for video in videos:

        video_id = video.video_id

        # 이미 만든 full_detail 로직 재사용
        full_data = await get_video_full_detail(video_id)

        results.append(full_data)

    return {"videos": results}