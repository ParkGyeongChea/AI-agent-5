template = """
# Role: Elite Edu-Designer & Tech Summarizer
# Task: Process `{transcript_data}` (auto-correct phonetic STT errors contextually, e.g., "치즈피트" -> "ChatGPT") to output an entity-dense Korean summary and logical chapters.

# Rules: Chain of Density (CoD) Summary
- Target: Final summary ≤{max_words} words.
- Flow: Draft base -> {iterations} densification steps. Add {entity_range} tech entities per step.
- Constraint: Fuse ALL past+new entities. Cut fillers. NEVER drop prior entities. Ensure proper tech terminology despite STT noise.
- Format: Use Markdown syntax for the final Korean output.

# Rules: Timeline Segmentation
- Chapters: 4-8 total (concept-based, adapt to length).
- Start: Exact "MM:SS" from transcript.
- Title: Professional Korean ("1. Title").

# Output Format
Strict minified JSON ONLY. Zero meta-text.
{{"summary":"<final_dense_korean_markdown_summary>","timeline":[{{"start":"MM:SS","title":"1. KR_Title"}}]}}
"""

def generate_prompt(transcript_data:str, max_words:int=200, entity_range="3~5", iterations:int=3) -> str:
    """챕터 분할을 위한 프롬프트 반환

    Args:
        transcript_data (str): 타임라인 기반 자막(스크립트) 데이터

    Returns:
        str: 프롬프트 리턴
    """
    return template.format(
        transcript_data = transcript_data,
        max_words = max_words,
        entity_range = entity_range,
        iterations = iterations
    )