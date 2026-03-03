
# YouTube API 연동 서비스

# - YouTube Data API 호출
# - 영상 검색
# - 영상 데이터 가공
# - 썸네일, 제목, 설명 정리

# ※ 외부 API 통신 로직은 이 파일에서 관리한다.

import yt_dlp
from schemas.youtube_schema import YouTubeInfo, YouTubeMetaData
from typing import List
from fastapi import HTTPException


def get_video_list(query: str, count: int = 3) -> List[YouTubeInfo]:

    try:
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)

        return [
            YouTubeInfo(
                video_id=video.get("id", ""),
                title=video.get("title", ""),
                url=video.get("webpage_url", "")
            )
            for video in info.get("entries", [])
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_video_data(video_id: str) -> YouTubeMetaData:

    try:
        url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        return YouTubeMetaData(
            video_id=info.get("id", ""),
            title=info.get("title", ""),
            channel_name=info.get("uploader", ""),
            description=info.get("description", ""),
            thumbnail_url=info.get("thumbnail"),
            chapters=info.get("chapters") or [],
            tags=info.get("tags") or []
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))