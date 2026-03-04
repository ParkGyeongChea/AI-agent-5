# 요청(Request) / 응답(Response) 데이터 구조 정의

# - Pydantic BaseModel 정의
# - API 입력값 검증
# - API 출력 형식 통일

# ※ 데이터 구조만 정의하고 로직은 작성하지 않는다.

# class RequestData(BaseModel):
#     query: str

# 이런 것만 작성

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class YouTubeInfo(BaseModel):
    """유튜브 기본 정보"""
    video_id:str = Field(description="영상 id")
    title:str = Field(description="영상 제목")
    url:str = Field(description="영상 url")

class YouTubeTimeLineTranscribe(BaseModel):
    """유튜브 타임라인 자막 정보"""
    timelines:List[Dict[str, str]] = Field(description="타임라인 자막 - {'start': '00:00', 'text': '안녕하세요.'} ")
    
    def get_full_transcript(self) -> str:
        """자막 텍스트를 반환

        Returns:
            str: 타임라인 기반 자막 텍스트 예 - "00:00) 안녕하세요."
        """
        full_text = ""
        for line in self.timelines:
            full_text += f"{line['start']}) {line['text']}\n"
        return full_text
    
class YouTubeChapters(BaseModel):
    """유튜브 챕터 정보"""
    data:List = Field(description="챕터 목록 - {'start': '00:00', 'title': '안녕하세요.'} ") 

class YouTubeMetaData(YouTubeInfo):
    """유튜브 메타 정보"""
    channel_name:str = Field(description="채널")
    description:str = Field(description="설명")
    thumbnail_url:str|None = Field(description="썸네일")
    chapters:YouTubeChapters = Field(description="챕터")
    tags:List[str] = Field(description="태그")

class YouTubeFullDetail(YouTubeMetaData):
    """유튜브 메타정보, 챕터, 자막을 모두 포함하는 종합 데이터"""
    
    timeLine_transcribe:YouTubeTimeLineTranscribe = Field(description="타임라인 자막 - {'start': '00:00', 'text': '안녕하세요.'} ")
    
    def get_full_transcript(self) -> str:
        """자막 텍스트를 반환

        Returns:
            str: 타임라인 기반 자막 텍스트 예 - "00:00) 안녕하세요."
        """
        full_text = ""
        transcribe = self.timeLine_transcribe
        for line in transcribe.timelines:
            full_text += f"{line['start']}) {line['text']}\n"
        return full_text