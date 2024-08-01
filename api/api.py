from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
from transformers import pipeline
from tempfile import NamedTemporaryFile

import cv2 as cv
import numpy as np
import os

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


def video_to_bytes(vid_file):
    vid_file = NamedTemporaryFile()
    vid_file.seek(0)
    yield from vid_file


def get_frames(video: cv.VideoCapture):
    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        yield frame


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
    temp_vid = NamedTemporaryFile(delete=False)
    temp_output_vid = NamedTemporaryFile(delete=False)

    try:
        # load video file
        # for each frame (as a coroutine?)
        #   apply model to frame
        #
        # print("Reading file...", end="")
        # content = await file.read()
        # print("Done")

        print("Creating pipeline...", end="")
        pipe = pipeline(task="depth-estimation", model=model)
        print("Done")

        print("Loading video...", end="")
        contents = await file.read()
        temp_vid.write(contents)
        cvvideo = cv.VideoCapture(temp_vid.name)

        width = int(cvvideo.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cvvideo.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(cvvideo.get(cv.CAP_PROP_FPS))

        fourcc = cv.VideoWriter_fourcc(*"XVID")
        output_video = cv.VideoWriter(
            "D:\\code\\ai\\ai-video-fx\\videos\\result.avi",
            fourcc,
            fps,
            (width, height),
        )
        print("Done")

        print("Processing frames...")
        current_frame = 1
        max_frames = int(cvvideo.get(cv.CAP_PROP_FRAME_COUNT))
        for frame in get_frames(cvvideo):
            print(f"...{current_frame}/{max_frames}")
            current_frame += 1

            # load frame as PIL image
            cvimg = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            frame = Image.fromarray(cvimg)

            # apply model to frame
            result = pipe(frame)["depth"]
            cvresult = np.array(result.convert("RGB"))

            # save result to videofile
            output_video.write(cvresult)
        print("Done")

        cvvideo.release()
        output_video.release()

        return {"path": "D:\\code\\ai\\ai-video-fx\\videos\\result.avi"}

        # return StreamingResponse(
        #     video_to_bytes(temp_output_vid), media_type="video/x-msvideo"
        # )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_vid.name)
        os.remove(temp_output_vid.name)
