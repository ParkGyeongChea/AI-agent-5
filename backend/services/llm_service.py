# LLM(GPT) 요약 및 생성 서비스

# - 영상 설명 요약
# - 질문 생성
# - AI 퀴즈 생성
# - OpenAI API 호출 담당
# ※ GPT 관련 로직은 모두 이 파일에서 관리한다.

# ChatOpenAI, LangChain, LangGraph 관련 코드는 여기
from prompts import timeline_summary_prompt, lecture_note_promp, quiz_prompt
import asyncio, time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def split_transcript_into_chunks(transcript_list, chunk_size=200):
    chunks = []
    for i in range(0, len(transcript_list), chunk_size):
        chunk = transcript_list[i:i + chunk_size]
        start = chunk[0]["start"]
        
        # 가능하면 데이터에 있는 실제 종료 시간 사용, 없다면 기존 로직 유지
        end = chunk[-1].get("end", chunk[-1]["start"]) 

        text = "\n".join(
            f"{line['start']}) {line['text']}"
            for line in chunk
        )

        chunks.append({
            "start": start,
            "end": end,
            "text": text
        })
    return chunks


def get_video_timeline_summary(transcript_data:str, max_words:int=200, entity_range="3~5", iterations:int=3):
    """자막을 기반으로 4~8개의 챕터를 생성하여 반환"""
    
    try:
        llm.bind(response_format={"type": "json_object"})
        
        # template = chapter_split_prompt.generate_prompt(transcript_data, max_words, entity_range, iterations)
        prompt = ChatPromptTemplate.from_template(timeline_summary_prompt.template)
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "transcript_data":transcript_data,
            "max_words":max_words,
            "entity_range":entity_range,
            "iterations":iterations
        })
        print(result)
        
        if "summary" not in result:
            result["summary"] = ""
        if "timeline" not in result or not isinstance(result["timeline"], list):
            result["timeline"] = []
            
    except Exception as e:
        print(e)
        
    return result



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
    try:
        chunks = split_transcript_into_chunks(transcript_data)
        
        semaphore = asyncio.Semaphore(5)
        async def process_chunk(chunk):
            async with semaphore:
                chunk_prompt = f"""
                Task: 다음은 영상의 {chunk['start']}부터 {chunk['end']}까지의 자막입니다. 
                이 구간의 핵심 내용을 2~3문장으로 요약해 주세요. 
                요약의 첫머리에는 반드시 시작 시간({chunk['start']})을 표기해 주세요.
                
                [자막]
                {chunk['text']}
                """
                return await llm.ainvoke(chunk_prompt)

        tasks = [process_chunk(chunk) for chunk in chunks]
        responses = await asyncio.gather(*tasks)
        
        chunk_summaries = [resp.content.strip() for resp in responses]
        merged = "\n\n".join(chunk_summaries)

        final_prompt = f"""
        Role: YT Analyst
        Task: Generate 4-10 chronological chapters from transcript.
        Input: {merged}
        
        Condition: 
        - If input is empty/null: "summary": "자막소스가 제공되지 않습니다.", "timeline": [].
        - Else: 4-5 line overview & 4-10 major chapter titles.
        
        Output Format (STRICT JSON ONLY): Korean.
        {{
            "summary": "overview text",
            "timeline": [
                {{"time": "MM:SS", "summary": "Chapter Title"}}
            ]
        }}
        """
        
        final_resp = await llm.ainvoke(final_prompt)
        
        # JsonOutputParser는 보통 알아서 ```json을 처리해주므로 바로 넘겨도 됩니다.
        # 혹시 모를 에러를 대비해 직접 파싱을 돕는다면 LLM 체인 형태로 묶는 것이 더 우아합니다.
        parser = JsonOutputParser()
        result = parser.invoke(final_resp)
        
        if "summary" not in result:
            result["summary"] = ""
        if "timeline" not in result or not isinstance(result["timeline"], list):
            result["timeline"] = []

        return result

    except Exception as e:
        return {
            "summary": "",
            "timeline": [],
            "error": str(e)
        }
    
    
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


# from core.llm_stats import OpenAIStats
def get_video_quzi(transcript_data:str):
    """
    유튜브 영상을 정리하여 프리미엄 강의 노트를 만든다.
    """
    
    try:
        # stats_runner = OpenAIStats()
        llm.bind(response_format={"type": "json_object"})
        prompt = ChatPromptTemplate.from_template(lecture_note_promp.template)
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({"transcript_data":transcript_data})
        # result, stats = stats_runner.run_llm(
        #     llm=chain,
        #     input={"transcript_data": transcript_data}
        # )
        # print(stats)
        
    except Exception as e:
        print(e)
        result = None
        
    return result


def get_video_quiz(lecture_content:str, difficulty:str="Mid", num_questions:int=5):
    """
    유튜브 영상의 내용을 파악하여 퀴즈를 생성한다.
    """
    
    try:
        # stats_runner = OpenAIStats()
        
        current_date = time.strftime("%Y-%m-%d %H:%M:%S")
        
        llm.bind(response_format={"type": "json_object"})
        prompt = ChatPromptTemplate.from_template(quiz_prompt.template)
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "lecture_content":lecture_content,
            "current_date":current_date,
            "difficulty":difficulty,
            "num_questions":num_questions,
        })
        
    except Exception as e:
        print(e)
        result = None
        
    return result