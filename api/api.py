from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
from transformers import pipeline
from tempfile import NamedTemporaryFile

import asyncio
import cv2 as cv
import numpy as np
import os


# constants
SUPPORTED_MODELS = [
    "LiheYoung/depth-anything-small-hf"
    # "prs-eth/marigold-depth-v1-0",
]

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
def temp_video_to_bytes(vid_file: str, delete_after: bool = True):
    with open(vid_file, "rb") as fp:
        yield from fp

    if delete_after:
        os.remove(vid_file)


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
    return {"models": SUPPORTED_MODELS}


@app.post("/generate")
async def post_generate(model: str, file: UploadFile):
    try:
        # create temp files to store the uploaded file and the resulting output file
        temp_upload = NamedTemporaryFile(delete=False, delete_on_close=False)
        temp_output = NamedTemporaryFile(
            suffix=".avi", delete=False, delete_on_close=False
        )
        temp_output.close()  # close immediately since opencv will open this with the writer

        print(temp_upload.name)
        print(temp_output.name)

        # open the uploaded file as a video using opencv
        uploaded_content = await file.read()
        temp_upload.write(uploaded_content)
        temp_upload.close()

        cv_video = cv.VideoCapture(temp_upload.name)

        # create the video writer
        width = int(cv_video.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cv_video.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(cv_video.get(cv.CAP_PROP_FPS))
        output_writer = cv.VideoWriter(
            temp_output.name,
            cv.VideoWriter_fourcc(*"XVID"),
            fps,
            (width, height),
        )

        # load the model
        if model == SUPPORTED_MODELS[0]:
            pipe = pipeline(task="depth-estimation", model=model)
        else:
            raise Exception("Unsupported model selected!")

        # iterate over each frame of the video
        print("Processing frames...")
        current_frame = 1
        max_frames = int(cv_video.get(cv.CAP_PROP_FRAME_COUNT))
        for frame in get_frames(cv_video):
            print(f"...{current_frame}/{max_frames}")
            current_frame += 1

            # load frame as PIL image so we can run it through the model
            pil_frame = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))

            # apply model to frame
            result = pipe(pil_frame)["depth"]
            cv_result = np.array(result.convert("RGB"))

            # save result to videofile
            output_writer.write(cv_result)
        print("Done")

        cv_video.release()
        output_writer.release()

        file_size = os.path.getsize(temp_output.name)
        return StreamingResponse(
            temp_video_to_bytes(temp_output.name, delete_after=False),
            media_type="video/x-msvideo",
        )
    except KeyboardInterrupt:
        print("Cancelling!")
        raise HTTPException(status_code=500, detail="Server aborted operation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_upload.name)
