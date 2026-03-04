
# LLM(GPT) 요약 및 생성 서비스

# - 영상 설명 요약
# - 질문 생성
# - AI 퀴즈 생성
# - OpenAI API 호출 담당

# ※ GPT 관련 로직은 모두 이 파일에서 관리한다.

# ChatOpenAI, LangChain, LangGraph 관련 코드는 여기
from schemas.youtube_schema import YouTubeChapters
from prompts import chapter_split_prompt

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def split_transcript_into_chunks(transcript_data: str, max_chars: int = 3000) -> list[str]:
    #자막 텍스트를 받아서, 3000글자 단위로 나누는 함수.
    
    
    """
    긴 자막 텍스트를 mas_chars 길이로 나눠서 chunk 리스트로 반환.
    """

    chunks = [] 
    start = 0
    
    while start < len(transcript_data):
    
        end = start + max_chars
        chunk = transcript_data[start:end]
        chunks.append(chunk)
        start = end
        
    return chunks




def chapter_split(transcript_data:str) -> YouTubeChapters:
    """자막을 기반으로 4~8개의 챕터를 생성하여 반환"""
        
    try:
        #1 자막을  chunk단위로 나누기
        chunks = split_transcript_into_chunks(transcript_data)
        #전체 자막 -> 3000글자 단위로 분할
        
        parser = JsonOutputParser()
        
        all_chapters = []
        # LLM 결과를 모을 리스트

        #2 chunk 반복
        
        for chunk in chunks:
            #청크 하나씩 LLM에게 보내기
            
            prompt = chapter_split_prompt.generate_prompt(chunk)
            #청크 데이터를 프롬프트에 삽입
            
            response = llm.invoke(prompt)
            #GPT 호출
            
            result = parser.parse(response.content)
            #LLM JSON 결과 파싱
            
            chapters = result.get("chapters", [])
            #LLM이 만든 챕터 리스트 가져오기
            
            all_chapters.extend(chapters)
            #모든 청크 결과를 하나의 리스트로 합치기

    except Exception as e:
        print(e)
        chapters = []   
        
    return YouTubeChapters(data=all_chapters)
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



def summarize_transcript(transcript_data: str) -> dict: #router에서 연결되는 함수. 영상 전체 요약+ 타임라인 요약 함수
    """
    자막을 기반으로 영상 전체 요약 + 타임라인 요약 생성 (chunk 기반)
    반환 예:
    {
      "summary": "...",
      "timeline": [{"time":"00:00","summary":"..."}, ...]
    }
    """

    try:
        # 1. 자막을 chunk로 쪼갠다 
        chunks = split_transcript_into_chunks(transcript_data)

        # 2. 각 chunk를 짧게 요약해서 누적한다
        chunk_summaries = []
        for idx, chunk in enumerate(chunks, start=1):
            chunk_prompt = f"""
            아래는 유튜브 영상 자막의 일부(조각)이다.

            [자막 조각 {idx}]
            {chunk}

            할 일:
            - 이 조각의 핵심 내용을 2~3줄로 한국어로 요약하라.
            - 반드시 '문장' 형태로만 출력하라. (JSON 금지)
            """
            resp = llm.invoke(chunk_prompt)
            chunk_summaries.append(resp.content.strip())

        # 3. 조각 요약들을 합쳐서 최종 요약 + 타임라인을 만든다 
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
        result = parser.parse(final_resp.content)

        # 4) 실패를 줄이기 위한 안전 기본값 보정
        if "summary" not in result:
            result["summary"] = ""
        if "timeline" not in result or not isinstance(result["timeline"], list):
            result["timeline"] = []

        return result

    except Exception as e:
        print(e)
        return {"summary": "", "timeline": []}