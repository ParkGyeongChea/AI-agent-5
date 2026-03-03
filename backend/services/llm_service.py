
# LLM(GPT) 요약 및 생성 서비스

# - 영상 설명 요약
# - 질문 생성
# - AI 퀴즈 생성
# - OpenAI API 호출 담당

# ※ GPT 관련 로직은 모두 이 파일에서 관리한다.

# ChatOpenAI, LangChain, LangGraph 관련 코드는 여기

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

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