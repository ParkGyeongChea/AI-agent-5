
# YouTube API 연동 서비스

# - YouTube Data API 호출
# - 영상 검색
# - 영상 데이터 가공
# - 썸네일, 제목, 설명 정리

# ※ 외부 API 통신 로직은 이 파일에서 관리한다.
import yt_dlp, requests
from schemas.youtube_schema import YouTubeInfo, YouTubeMetaData, YouTubeTimeLineTranscrabe, YouTubeChapter
from typing import List, Dict
from fastapi import HTTPException


def get_video_list(query: str, count: int = 3) -> List[YouTubeInfo]:
    """요청 갯수 만큼 유튜브 영상 리스트 반환"""

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

def get_video_metadata(video_id: str) -> YouTubeMetaData:
    """유튜브 영상 메타 정보 반환"""
    
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
            tags=info.get("tags") or [],
            url=url
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _parse_vtt(text) -> List[Dict]:
    """"vtt 파일 데이터 정제"""
    
    lines_data = []

    lines = text.split("\n")
    for i in range(len(lines)):
        if "-->" in lines[i]:
            timestamp = lines[i].strip()
            text = lines[i+1].strip()
            lines_data.append({
                "timestamp": timestamp,
                "text": text
            })

    return lines_data
    
    
def get_video_transcrabe(video_id:str):
    """유튜브 영상 자막 반환"""
    
    #  video_id = "rb3ZYR_Q1po" or "LcPrSL4sEOc" # 테스트용
    
    langs = ["ko", "en"]
    ydl_opts = {
        "writesubtitles": True,        # 일반 자막
        "writeautomaticsub": True,     # 자동 자막
        "subtitleslangs": langs,
        "subtitlesformat": "vtt",      # vtt 형식
        "skip_download": True,
        "quiet": True,                # 로그 출력 유무
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

        requested_subs = info.get('subtitles', {})      # 일반
        auto_subs = info.get('automatic_captions', {})  # 자동
        
        for lang in langs:
            subs = requested_subs.get(lang) or auto_subs.get(lang)
            if subs:
                # VTT 형식 자막 URL 가져오기
                sub_url = ""
                for sub in subs[langs[0]]:
                    if sub.get('ext') == 'vtt':
                        sub_url = sub['url']
                        print(f"[{langs[0]}]  vtt 자막 URL: {sub_url}")
                        break
                
                # 자막 요청
                res = requests.get(sub_url)
                
                # 자막 파싱
                vtt_data = _parse_vtt(res.text)
                
                timeline = []
                for line in vtt_data[1::2]:
                    timestamp = line["timestamp"].split(" --> ")[0]
                    h, m, s = timestamp.split(':')
                    m = int(h) * 60 + int(m)
                    timeline.append(
                        {
                            "start": f"{int(m)}:{int(float(s)):02}",
                            "text": line["text"]
                        }
                    )
                    
                YouTubeTimeLineTranscrabe(timeline=timeline)
        
    raise ValueError(f"자막 정보를 찾을 수 없습니다. 직접 구현 필요!")

def _format_time(seconds):
    """시간(초) -> 'MM:SS' 형식으로 변환"""
    
    # 몫(minutes)과 나머지(seconds)를 구함
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}:{secs:02}"

def get_video_chapter(video_id:str):
    """유튜브 영상 챕터 반환"""
    
    #  video_id = "rb3ZYR_Q1po" or "LcPrSL4sEOc" # 테스트용

    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        
    chapters = info.get("chapters") or []
    
    # 자동 챕터를 제공하는 경우 (챕터의 제목이 영어인 경우가 있음)
    if len(chapters) > 0:
        
        data = [
            {"start": _format_time(c.get("start_time", 0)), "title": c.get("title", "")}
            for c in chapters
        ]
        print(f"\n-------챕터: {data}")

    # 챕터를 직접 구현
    else:
        raise ValueError(f"챕터 정보를 찾을 수 없습니다. 직접 구현 필요!")
    
    return YouTubeChapter(chapters=data)
