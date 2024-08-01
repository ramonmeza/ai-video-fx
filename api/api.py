from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
from transformers import pipeline


# initialization
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


# functions
def image_to_bytes(image: Image):
    image_bytes = BytesIO()
    image.save(image_bytes, format="JPEG", quality=85)
    image_bytes.seek(0)
    yield from image_bytes


# routes
@app.get("/")
async def get_info():
    return {"version": "0.0.1"}


@app.get("/models")
async def get_models():
    return {
        "models": [
            "LiheYoung/depth-anything-small-hf",
            # "prs-eth/marigold-depth-v1-0",
        ]
    }


@app.post("/generate")
async def post_generate(model: str, file: UploadFile):
    try:
        # load video file
        # for each frame (as a coroutine?)
        #   apply model to frame
        #
        print("Reading file...", end="")
        content = await file.read()
        print("Done")

        print("Creating pipeline...", end="")
        pipe = pipeline(task="depth-estimation", model=model)
        print("Done")

        print("Loading image...", end="")
        image = Image.open(BytesIO(content))
        print("Done")

        print("Generating depth...", end="")
        result = pipe(image)["depth"]
        print("Done")

        return StreamingResponse(image_to_bytes(result), media_type="image/jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
