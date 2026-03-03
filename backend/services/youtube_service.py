
# YouTube API 연동 서비스

# - YouTube Data API 호출
# - 영상 검색
# - 영상 데이터 가공
# - 썸네일, 제목, 설명 정리

# ※ 외부 API 통신 로직은 이 파일에서 관리한다.

import yt_dlp
from schemas.youtube_schema import YouTubeInfo, YouTubeMetaData
from typing import List, Dict, Optional


def get_video_list(query:str, count:int=3) -> List[YouTubeInfo]:
    """질의를 통해 요청 갯수만큼 관련 영상 리스트 반환

    Args:
        query (str): 사용자 질문
        count (int, optional): 요청 갯수. Defaults to 3.
    """
    
    print(f"\n---------------{query}---------------")
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)
    
    infos = []
    for video in info["entries"]:
        print(f'{video["title"]}')
        infos.append(
            YouTubeInfo(video_id=video["id"], title=video["title"], url=video["webpage_url"])
        )
    return infos

def get_video_data(video_id:str) -> YouTubeMetaData:
    """요청한 id의 유튜브 영상의 메타데이터를 반환합니다.
    id: 비디오 ID,
    title: 제목,
    uploader: 채널명,
    duration:영상길이,
    upload_date: 업로드일,
    thumbnail: 썸네일,

    Args:
        video_id (str): _description_

    Returns:
        _type_: _description_
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        data = YouTubeMetaData(
            video_id=info.get('id'),
            title=info.get('title', ""),
            channel_name=info.get("uploader", ""),
            description=info.get("description", ""),
            thumbnail_url=info.get("thumbnail", ""),
            chapters=info.get("chapters") or [],
            tags=info.get("tags") or []
        )
        print(data)
        return data