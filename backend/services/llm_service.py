# LLM(GPT) 요약 및 생성 서비스

# - 영상 설명 요약
# - 질문 생성
# - AI 퀴즈 생성
# - OpenAI API 호출 담당
# ※ GPT 관련 로직은 모두 이 파일에서 관리한다.

# ChatOpenAI, LangChain, LangGraph 관련 코드는 여기
from schemas.youtube_schema import YouTubeTimeLine
from prompts import chapter_split_prompt
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def split_transcript_into_chunks(transcript_list: list, chunk_size: int = 200):
    #추후에 token chunk 로 변경될 수도 있음
    
    """
    자막 리스트를 chunk_size 단위로 나누는 함수
    
    transcript_list 예:
    [
        {"start":"00:00","text":"안녕하세요"},
        {"start":"00:02","text":"오늘은"}
    ]
    """
    chunks = []
    
    for i in range(0, len(transcript_list), chunk_size):
        
        chunk = transcript_list[i:i + chunk_size]
        
        text = ""
        for line in chunk:
            text += f"{line['start']}) {line['text']}\n"
            
        chunks.append(text)
            
    return chunks


def chapter_split(transcript_data:list) -> YouTubeTimeLine:
    """자막을 기반으로 4~8개의 챕터를 생성하여 반환"""
        
    try:
        transcript_list = transcript_data
        chunks = split_transcript_into_chunks(transcript_list)
    
        parser = JsonOutputParser()
        
        all_chapters = []     
        
        for chunk in chunks:
                     
            prompt = chapter_split_prompt.generate_prompt(chunk)   
            response = llm.invoke(prompt) 
            result = parser.parse(response.content)
            chapters = result.get("chapters", [])      
            all_chapters.extend(chapters)
            

    except Exception as e:
        print(e)
        chapters = []   
        
    return YouTubeTimeLine(timelines=all_chapters)
    #fastAPI schema 형태로 변환



def summarize_video(title: str, description: str) -> str:

    prompt = f"""
    다음은 유튜브 영상 정보이다.

    제목 : {title}
    설명 : {description}

    1. 영상 전체 요약을 4~5줄로 작성하라.
    2. 5분 단위 타임라인 요약을 3개 작성하라.

    반드시 JSON 형식으로만 출력하라.
    """

    response = llm.invoke(prompt)
    return response.content



async def summarize_transcript(transcript_data: list) -> dict: 
    """
    자막을 기반으로 영상 전체 요약 + 타임라인 요약 생성 (chunk 기반)
    반환 예:
    {
      "summary": "...",
      "timeline": [{"time":"00:00","summary":"..."}, ...]
    }
    """

    try:
        
        transcript_list = transcript_data
        chunks = split_transcript_into_chunks(transcript_list)

       
        tasks = []
        
        for idx, chunk in enumerate(chunks, start=1):
            chunk_prompt = f"""
            아래는 유튜브 영상 자막의 일부(조각)이다.

            [자막 조각 {idx}]
            {chunk}

            할 일:
            - 이 조각의 핵심 내용을 2~3줄로 한국어로 요약하라.
            - 반드시 '문장' 형태로만 출력하라. (JSON 금지)
            """
            
            tasks.append(llm.ainvoke(chunk_prompt))
            
        responses = await asyncio.gather(*tasks)
        
        chunk_summaries = [
             resp.content.strip()
             for resp in responses
        ]

        
        merged = "\n".join(chunk_summaries)

        final_prompt = f"""
        아래는 유튜브 영상 자막을 여러 조각으로 나눠 요약한 결과 모음이다.

        {merged}

        위 내용을 바탕으로 아래 JSON 형식으로만 출력하라.

        {{
          "summary": "영상 전체 요약 (4~5줄)",
          "timeline": [
            {{"time":"00:00","summary":"내용"}},
            {{"time":"05:00","summary":"내용"}},
            {{"time":"10:00","summary":"내용"}}
          ]
        }}
        """

        parser = JsonOutputParser()
        final_resp = llm.invoke(final_prompt)
        content = final_resp.content.replace("```json", "").replace("```", "")
        result = parser.parse(content)

        
        if "summary" not in result:
            result["summary"] = ""
        if "timeline" not in result or not isinstance(result["timeline"], list):
            result["timeline"] = []

        return result

    except Exception as e:
        print(e)
        return {"summary": "", "timeline": []}
    
    
##########

def summarize_videos(videos: list):

    prompt = "다음 유튜브 영상들을 요약해라.\n\n"

    for idx, video in enumerate(videos, start=1):
        prompt += f"""
영상 {idx}
제목: {video['title']}
설명: {video['description']}
"""

    prompt += """
각 영상의 핵심 내용을 3줄로 요약하라.

JSON 형식으로 출력하라.

[
 {"summary": "..."},
 {"summary": "..."},
 {"summary": "..."}
]
"""

    response = llm.invoke(prompt)

    parser = JsonOutputParser()

    result = parser.parse(response.content)

    return [item["summary"] for item in result]