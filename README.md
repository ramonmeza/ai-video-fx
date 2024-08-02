# AI Video FX

An application that leverages the power of AI models to manipulate frames of a video file.

## About
I wanted to learn about using AI models and found a few depth models that produce interesting results when given an image. I wanted to create an application that would make it simple for me to upload a video to be processed through these AI models and the result to be saved.

## Supported Models

### LiheYoung/depth-anything-small-hf
_[Hugging Face Repo](https://huggingface.co/LiheYoung/depth-anything-small-hf)_

Input:
![Input](docs/input.gif)

Result:
![Result](docs/result.gif)


## Running the application and API

![Web UI](./docs/form.jpg)

### Run UI
The front-end UI was developed using React and Next.js. The UI will run on `localhost:3000` by default.

Note: `API_URL` is defined as a constant in `app\page.js`. If you want to run the API on a different port or with a different URL, modify the value for `API_URL`. This will eventually change to building the static site using Next.js SSG.

```
npx next dev
// npx next build
```

### Run API
The API was developed using FastAPI and will run on `localhost:8000` by default.

```
fastapi dev api/api.py
```