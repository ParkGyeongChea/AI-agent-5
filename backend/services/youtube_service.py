
# YouTube API 연동 서비스

# - YouTube Data API 호출
# - 영상 검색
# - 영상 데이터 가공
# - 썸네일, 제목, 설명 정리

# ※ 외부 API 통신 로직은 이 파일에서 관리한다.

import yt_dlp, requests
from backend.core.config import MAX_VIDEO_DURATION_SECODS # 추가
from backend.schemas.youtube_schema import YouTubeInfo, YouTubeMetaData, YouTubeTranscribe, YouTubeFullDetail, YouTubeTimeLine
from typing import List, Dict
from fastapi import HTTPException

#######################################################################
# 영상 시간 제한 추가 함수 ,26 3.5 추가

def get_video_list(query: str, count: int = 3) -> List[YouTubeInfo]:

    try:
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)

            results = []
        
            for video in info.get("entries", []):
                
                duration = video.get("duration",0)

                #30분 이상 영상은 제외
                if duration > MAX_VIDEO_DURATION_SECODS:
                    continue
                results.append(
                    YouTubeInfo(
                        video_id=video.get("id", ""),
                        title=video.get("title", ""),
                        url=video.get("webpage_url", ""),
                        thumbnail_url=f"https://img.youtube.com/vi/{video.get('id', '')}/0.jpg",
                        description=video.get("description", "") or "" #3.6추가, 검색 결과에서 설명을 같이 담음
                    )
                )
                #개수 채우면 종료
                if len(results) == count:
                    break
            return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#######################################################################

         

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

            subtitle_text = ""

            # 다음 줄 존재 확인 함수
            if i + 1 < len(lines):
                subtitle_text = lines[i+1].strip()

            if subtitle_text:
                lines_data.append({
                    "timestamp": timestamp,
                    "text": subtitle_text
                })

    return lines_data
    
def get_video_transcribe(video_id: str):
    """유튜브 영상 자막 반환"""
    
    # 테스트용 id
    # "rb3ZYR_Q1po" - 챕터 없음, 자막 있음
    # "LcPrSL4sEOc" - 챕터 있음, 자막 없음
    #  PzeQ-H9q3Y8
    
    langs = ["ko", "en"]
    ydl_opts = {
        "writesubtitles": True,        # 일반 자막
        "writeautomaticsub": True,     # 자동 자막
        "subtitleslangs": langs,
        "subtitlesformat": "vtt",      # vtt 형식
        "skip_download": True,
        "quiet": True,                 # 로그 출력 유무
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        
        
    
        requested_subs = info.get('subtitles', {})      # 일반
        auto_subs = info.get('automatic_captions', {})  # 자동
        
        for lang in langs:
            # 해당 언어의 자막 리스트 가져오기 (일반 자막 우선)
            subs = requested_subs.get(lang) or auto_subs.get(lang)
            
            if subs:
                sub_url = ""
                
                for sub in subs:
                    if sub.get('ext') == 'vtt':
                        sub_url = sub['url']
                        # 2. 현재 찾은 언어(lang)를 정확히 출력합니다.
                        print(f"[{lang}] vtt 자막 URL: {sub_url}")
                        break
                
                if sub_url:
                    res = requests.get(sub_url)
                    vtt_data = _parse_vtt(res.text)
                    
                    timeline = []
                    for line in vtt_data[1::2]:
                        timestamp = line["timestamp"].split(" --> ")[0]                        
                        h, m, s = timestamp.split(':')
                        m = int(h) * 60 + int(m)
                        timeline.append({
                            "start": f"{int(m):02}:{int(float(s)):02}",
                            "title": line["text"]
                        })
                    return YouTubeTranscribe(
                        transcript=timeline
                    )
    print(f"\n-------자막 정보를 찾을 수 없습니다. 직접 구현 필요!")
    return YouTubeTranscribe(transcript=[])

def _format_time(seconds):
    """시간(초) -> 'MM:SS' 형식으로 변환"""
    
    # 몫(minutes)과 나머지(seconds)를 구함
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02}:{secs:02}"

def get_video_timeline(video_id:str):
    """유튜브 영상 챕터 반환"""
    
    # 테스트용 id
    # "rb3ZYR_Q1po" - 챕터 없음, 자막 있음
    # "LcPrSL4sEOc" - 챕터 있음, 자막 없음

    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        
    chapters = info.get("chapters") or []
    data = []
    # 자동 챕터를 제공하는 경우 (챕터의 제목이 영어인 경우가 있음)
    if len(chapters) > 0:
        
        data = [
            {"time": _format_time(c.get("start_time", 0)), "summary": c.get("title", "")}
            for c in chapters
        ]
        print(f"\n-------챕터: {data}")

    # 챕터를 직접 구현
    else:
        print(f"\n-------챕터 정보를 찾을 수 없습니다. 직접 구현 필요!")
    
    return YouTubeTimeLine(timelines=data)


def get_video_full_detail(video_id:str):
    """유튜브 영상의 자막, 챕터, 메타 정보를 한 번에 반환"""
    
    # 테스트용 id
    # "rb3ZYR_Q1po" - 챕터 없음, 자막 있음
    # "LcPrSL4sEOc" - 챕터 있음, 자막 없음
    
    langs = ["ko", "en"]
    ydl_opts = {
        "writesubtitles": True,        # 일반 자막
        "writeautomaticsub": True,     # 자동 자막
        "subtitleslangs": langs,
        "subtitlesformat": "vtt",      # vtt 형식
        "skip_download": True,
        "quiet": False,                # 로그 출력 유무
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        
        # 자막
        requested_subs = info.get('subtitles', {})      # 일반
        auto_subs = info.get('automatic_captions', {})  # 자동
        
        sub_url = None
        for lang in langs:
            # 일반 자막을 먼저 확인하고, 없으면 자동 자막 리스트 사용
            subs_list = requested_subs.get(lang) or auto_subs.get(lang)
            
            if subs_list:  # 해당 언어의 자막 리스트가 존재하면
                # 리스트 안에서 VTT 형식 자막 URL 찾기
                for sub in subs_list:
                    if sub.get('ext') == 'vtt':
                        sub_url = sub['url']
                        print(f"\n-------[{lang}] vtt 자막 URL: {sub_url}")
                        break
                        
            if sub_url:
                break  # 우선순위가 높은 언어의 자막을 찾았으므로 언어 검색 루프 전체 종료
            
        # 자막 요청
        timelines = []
        if sub_url:
            res = requests.get(sub_url)
            
            # 자막 파싱
            vtt_data = _parse_vtt(res.text)
            for line in vtt_data[1::2]:
                timestamp = line["timestamp"].split(" --> ")[0]
                h, m, s = timestamp.split(':')
                m = int(h) * 60 + int(m)
                timelines.append(
                    {
                        "start": f"{int(m):02}:{int(float(s)):02}",
                        "text": line["text"]
                    }
                )
        else:
            print(f"\n-------자막 정보를 찾을 수 없습니다. 직접 구현 필요!")
            
        timeLine_transcribe = YouTubeTranscribe(
            transcript=timelines
        )
        
        return YouTubeFullDetail(
            video_id=info.get("id", ""),
            title=info.get("title", ""),
            channel_name=info.get("uploader", ""),
            description=info.get("description", ""),
            thumbnail_url=info.get("thumbnail"),
            url=info.get("webpage_url", ""),
            transcribe=timeLine_transcribe
        )