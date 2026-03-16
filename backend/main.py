
# FastAPI 서버 실행 


from fastapi import FastAPI
from api.youtube_router import router as youtube_router

app = FastAPI()

app.include_router(youtube_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)