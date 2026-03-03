
# FastAPI 서버 실행 진입점 (Entry Point)

# - uvicorn으로 실행되는 시작 파일
# - 전체 FastAPI 앱 생성
# - router 등록
# - 서버 실행 담당

# ※ 실제 비즈니스 로직은 여기 작성하지 않는다.
# ※ 서비스 로직은 services/ 폴더에서 관리한다.

from schemas.youtube_schema import YouTubeInfo, YouTubeMetaData
from typing import List, Dict, Optional
from services import youtube_service as youtube

from fastapi import FastAPI 
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

import os
import requests 

from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

llm = ChatOpenAI(        
    model="gpt-4o-mini",
    temperature=0
)

app = FastAPI()
class RequestData(BaseModel):
    query:str


def search_youtube(query:str):
    url = "https://www.googleapis.com/youtube/v3/search"
    params ={ 
        "part" : "snippet",
        "q" : f"{query} 한국어",
        "key" : YOUTUBE_API_KEY,
        "maxResults" : 5, 
        "relevanceLanguage": "ko", 
        
        "type" : "video"    
    }
    response = requests.get(url, params=params) 
    data = response.json() 
    
    videos = []
    
    for item in data.get("items", [])[:5]: 
        video_id = item["id"]["videoId"] 
        title = item["snippet"]["title"] 
        description = item["snippet"]["description"] 
        
        
        
        description = description[:120] +'...' if len(description) > 120 else description
        
        
        
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
        
        videos.append({ 
            "title":title,
            "url":f"https://www.youtube.com/watch?v={video_id}",
            "description": description,
            "thumbnail" : thumbnail
        })
    return videos 


def summarize_video(title: str, description: str):
    
    prompt = f"""
    다음은 유튜브 영상 정보이다.
    
    제목 : {title}
    설명 : {description}
    
    1.영상 전체 요약을 4~5줄로 작성하라.
    2.5분 단위 타임라인 요약을 3개 작성하라.
    
    반드시 아래 json형식으로만 출력하라:
    
    {{
        "summary": "전체 요약",
        "timeline_summary": [
            {{"time": "00:00", "content": "..."}},
            {{"time": "05:00", "content": "..."}},
            {{"time": "10:00", "content": "..."}}
        ]
    }}
    """
    
    response = llm.invoke(prompt)
    
    return response.content



@app.post("/recommend") 
def recommend(data:RequestData): 
    
    videos = search_youtube(data.query)
    
    result = []

    for video in videos:
        summary_text = summarize_video(
            video["title"],
            video["description"]
        )

        result.append({
            "title": video["title"],
            "url": video["url"],
            "description": video["description"],
            "thumbnail": video["thumbnail"],
            "llm_output": summary_text
        })
        
    return {"videos":result}




@app.get("/chat/search/{query}", response_model=List[YouTubeInfo])
def get_video_infos(query:str):
    
    lists = youtube.get_video_list(query=query)
    return lists

@app.get("/video/{viedo_id}", response_model=YouTubeMetaData)
def get_video_data(viedo_id:str):
    return youtube.get_video_data(video_id=viedo_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)






