from diffusers import (
    StableDiffusionInstructPix2PixPipeline,
    StableDiffusionImageVariationPipeline,
    EulerAncestralDiscreteScheduler,
)
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image
from transformers import pipeline
from tempfile import NamedTemporaryFile
from typing import Optional

import asyncio
import cv2 as cv
import numpy as np
import os
import torch
from torchvision import transforms


# constants
SUPPORTED_MODELS = [
    "LiheYoung/depth-anything-small-hf",
    "AnalogMutations/instruct-pix2pix",
    "lambdalabs/sd-image-variations-diffusers",
    # "prs-eth/marigold-depth-v1-0",
]

CODECC: str = "X264"
CODECC_SUFFIX: str = ".mp4"
CODECC_MEDIATYPE: str = "video/mp4"


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


async def remove_file(file_path):
    while True:
        try:
            await asyncio.sleep(5)
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")
            break
        except:
            pass


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
async def post_generate(
    model: str,
    file: UploadFile,
    prompt: Optional[str] = "turn him into a cyborg",
    guidance: Optional[float] = 7,
    num_inference_steps: Optional[int] = 10,
):
    try:
        print(
            {
                "model": model,
                "prompt": prompt,
                "guidance": guidance,
                "num_inference_steps": num_inference_steps,
            }
        )

        # create temp files to store the uploaded file and the resulting output file
        temp_upload = NamedTemporaryFile(delete=False, delete_on_close=False)
        temp_output = NamedTemporaryFile(
            suffix=CODECC_SUFFIX, delete=False, delete_on_close=False
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
            cv.VideoWriter_fourcc(*CODECC),
            fps,
            (width, height),
        )

        # load the model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if model == "LiheYoung/depth-anything-small-hf":
            pipe = pipeline(device=device, task="depth-estimation", model=model)
        elif model == "AnalogMutations/instruct-pix2pix":
            pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
                model, torch_dtype=torch.float16, safety_checker=None
            ).to(device)
            pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
                pipe.scheduler.config
            )
        elif model == "lambdalabs/sd-image-variations-diffusers":
            pipe = StableDiffusionImageVariationPipeline.from_pretrained(
                model,
                revision="v2.0",
            ).to(device)
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
            if model == "LiheYoung/depth-anything-small-hf":
                result = pipe(pil_frame)["depth"]
            elif model == "AnalogMutations/instruct-pix2pix":
                result = (
                    pipe(
                        prompt,
                        image=pil_frame,
                        num_inference_steps=num_inference_steps,
                        image_guidance_scale=guidance,
                    )
                    .images[0]
                    .convert("RGB")
                )
            elif model == "lambdalabs/sd-image-variations-diffusers":
                result = pipe(pil_frame, guidance_scale=guidance)["images"][0].convert(
                    "RGB"
                )

            cv_result = np.array(cv.cvtColor(np.array(result), cv.COLOR_RGB2BGR))

            # save result to videofile
            output_writer.write(cv_result)
        print("Done")

        cv_video.release()
        output_writer.release()

        return StreamingResponse(
            temp_video_to_bytes(temp_output.name, delete_after=True),
            media_type=CODECC_MEDIATYPE,
        )

    except KeyboardInterrupt:
        print("Cancelling!")
        raise HTTPException(status_code=500, detail="Server aborted operation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await remove_file(temp_upload.name)
