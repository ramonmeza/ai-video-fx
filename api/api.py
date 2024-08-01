from asyncio import sleep

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def get_info():
    return {"version": "0.0.1"}


@app.get("/models")
async def get_models():
    return {
        "models": [
            "prs-eth/marigold-depth-v1-0",
            "LiheYoung/depth-anything-small-hf",
        ]
    }


@app.post("/generate")
async def post_generate(model: str, file: UploadFile):
    await sleep(10)
    return {"model": model, "filename": file.filename}
