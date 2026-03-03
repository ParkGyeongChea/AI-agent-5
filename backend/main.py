
# FastAPI 서버 실행 진입점 (Entry Point)

# - uvicorn으로 실행되는 시작 파일
# - 전체 FastAPI 앱 생성
# - router 등록
# - 서버 실행 담당

# ※ 실제 비즈니스 로직은 여기 작성하지 않는다.
# ※ 서비스 로직은 services/ 폴더에서 관리한다.


from fastapi import FastAPI
from api.youtube_router import router as youtube_router

app = FastAPI()

app.include_router(youtube_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)