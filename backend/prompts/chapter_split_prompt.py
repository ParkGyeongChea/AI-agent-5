template = """
Role: Elite Edu-Designer/Analyst.
Task: Segment transcript into 4-8 logical chapters based on concepts.

Rules:
1. Chapters: 4-8 total(Adjust according to video length.)
2. Timing: 'start' MUST be "MM:SS" from transcript.
3. Language: 'title' in professional Korean.

JSON STRUCTURE EXAMPLE: 
{{
    "chapters":
    [
        {{"start": "MM:SS", "title": "number. KR_Title"}}, 
        ...
    ]
}}
Transcript: {transcript_data}
"""

def generate_prompt(transcript_data:str) -> str:
    """챕터 분할을 위한 프롬프트 반환

    Args:
        transcript_data (str): 타임라인 기반 자막(스크립트) 데이터

    Returns:
        str: 프롬프트 리턴
    """
    return template.format(
        transcript_data = transcript_data
    )