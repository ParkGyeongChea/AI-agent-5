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

from schemas.youtube_schema import YouTubeInfo, YouTubeMetaData, YouTubeTimeLineTranscrabe, YouTubeChapter
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

@router.post("/video/info/transcribe/{viedo_id}", response_model=YouTubeTimeLineTranscrabe)
async def get_transcrabe(viedo_id:str):
    return youtube_service.get_video_transcrabe(viedo_id)

@router.post("/video/info/chapter/{viedo_id}", response_model=YouTubeChapter)
async def get_video_chapter(viedo_id:str):
    return youtube_service.get_video_chapter(viedo_id)


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