from fastapi import FastAPI
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
async def get_root():
    return {"Hello": "World"}


@app.get("/models")
async def get_models():
    return {
        "models": [
            "prs-eth/marigold-depth-v1-0",
            "LiheYoung/depth-anything-small-hf",
        ]
    }
