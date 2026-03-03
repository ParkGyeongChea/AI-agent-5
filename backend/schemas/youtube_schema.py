# 요청(Request) / 응답(Response) 데이터 구조 정의

# - Pydantic BaseModel 정의
# - API 입력값 검증
# - API 출력 형식 통일

# ※ 데이터 구조만 정의하고 로직은 작성하지 않는다.

# class RequestData(BaseModel):
#     query: str

# 이런 것만 작성

from pydantic import BaseModel
from typing import List


class YouTubeInfo(BaseModel):
    video_id: str
    title: str
    url: str


class YouTubeMetaData(BaseModel):
    video_id: str
    title: str
    channel_name: str
    description: str
    thumbnail_url: str | None
    chapters: list
    tags: list
