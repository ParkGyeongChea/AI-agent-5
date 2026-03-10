

from pydantic import BaseModel, Field
from typing import List, Dict

class YouTubeInfo(BaseModel):
    """유튜브 기본 정보"""
    video_id:str = Field(description="영상 id")
    title:str = Field(description="영상 제목")
    url:str = Field(description="영상 url")
    thumbnail_url:str|None = Field(description="썸네일")
    description:str = Field(default="", description="영상 설명") #3.6 코드 추가, 검색 결과만으로 추천 요약 가능
    channel_name:str = Field(description="채널")
    duration:int = Field(description="영상길이(초)")
    
class YouTubeTimeLine(BaseModel):
    timelines:List[Dict[str, str]] = Field(description="타임라인 자막 - {'start': '00:00', 'title': '안녕하세요.'} ")

class YouTubeTranscribe(BaseModel):
    """유튜브 타임라인 자막 정보"""
    transcript:List[Dict[str, str]] = Field(description="타임라인 자막 - {'start': '00:00', 'text': '안녕하세요.'} ")
    
    def get_full_transcript(self) -> str:
        """자막을 텍스트로 반환"""
        full_text = ""
        for line in self.transcript:
            full_text += f"{line['start']}) {line['text']}\n"
        return full_text

# class YouTubeMetaData(YouTubeInfo):
#     """유튜브 메타 정보"""
#     description:str = Field(description="설명")    
#     channel_name:str = Field(description="채널")

class YouTubeFullDetail(BaseModel):
    """유튜브 메타정보, 챕터, 자막을 모두 포함하는 종합 데이터"""
    
    transcribe:YouTubeTranscribe = Field(description="타임라인 자막 - {'start': '00:00', 'text': '안녕하세요.'} ")
    
    summary: str | None = None
    timeline: List[Dict] | None = None
    
    def get_full_transcript(self) -> str:
        """자막 텍스트를 반환

        Returns:
            str: 타임라인 기반 자막 텍스트 예 - "00:00) 안녕하세요."
        """
        full_text = ""
        for line in self.transcribe.transcript:
            full_text += f"{line['start']}) {line['text']}\n"
        return full_text