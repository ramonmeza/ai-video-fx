"use client";

import React, { useState, useEffect } from "react";
import Spinner from "./spinner";
import Slider from "./slider";

const API_URL = "http://localhost:8000"

export default function Home() {
  const [models, setModels] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [result, setResult] = useState(null);
  const [resultMimeType, setResultMimeType] = useState(null);
  const [resultFilename, setResultFilename] = useState(null);
  const [submittingForm, setSubmittingForm] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/models`)
      .then(response => response.json())
      .then(json => setModels(json["models"]))
      .catch(error => console.error(error));
  }, []);

  async function submitForm(event) {
    event.preventDefault();

    const selected_filename = document.getElementById("file").value;
    if (!selected_filename) {
      alert("Please select a file!");
      return;
    }

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    setSubmittingForm(true);
    setResult(null);
    setResultMimeType(null);
    setResultFilename(null);

    const model = formData.get("model");
    const prompt = formData.get("prompt");
    const guidance = formData.get("guidance");
    const num_inference_steps = formData.get("num_inference_steps");

    const urlparams = `model=${model}` +
      (prompt ? `&prompt=${prompt}` : "") +
      (guidance ? `&guidance=${guidance}` : "") +
      (num_inference_steps ? `&num_inference_steps=${num_inference_steps}` : "");

    const response = await fetch(`${API_URL}/generate?${urlparams}`, {
      method: "POST",
      body: formData
    }).catch(error => console.error(error));

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setResult(url);
      setResultMimeType(response.headers.get("content-type"));
      // setResultFilename(response.headers.get("filename"));
      setResultFilename("result.mp4");

    } else {
      setResult(null);
      console.error("Failed to download file");
    }

    setSubmittingForm(false);
  }

  return (
    <main>
      <div className="container mx-auto bg-gray-200 py-4">
        <div className="flex flex-col text-center px-4 md:px-8">
          <h1 className="text-3xl font-semibold">Apply AI Model to Video</h1>
          <p className="italic text-lg text-slate-600">
            The process is simple; just upload your video file, select a model, then press submit!
          </p>
        </div>

        <form id="uploadForm" method="POST" encType="multipart/form-data">
          <div className="flex flex-col justify-center gap-4 p-4 md:p-8">
            <div>
              <label htmlFor="file" className="text-xl block mb-2">Select a video file</label>
              <input type="file" name="file" id="file" className="block" accept="video/*" />
            </div>

            <div>
              <label htmlFor="model" className="text-xl block mb-2">Select a model: </label>
              <select className="form-select min-w-full" id="model" name="model" onChange={() => { setSelectedModel(document.getElementById("model").value); }}>
                {
                  models ? models.map((model, index) => {
                    return (
                      <option key={index}>
                        {model}
                      </option>
                    );
                  }) : <option>Loading...</option>
                }
              </select>
            </div>

            {
              selectedModel == "AnalogMutations/instruct-pix2pix" ?
                <>
                  <div>
                    <label htmlFor="prompt" className="text-xl block mb-2">Prompt</label>
                    <input type="text" id="prompt" name="prompt" placeholder="Turn him into a cyborg"></input>
                  </div>
                  <div>
                    <label htmlFor="guidance" className="text-xl block mb-2">Guidance</label>
                    <Slider id="guidance" name="guidance" minValue={5} maxValue={15} defaultValue={8} step={1} className="slider" />
                  </div>
                  <div>
                    <label htmlFor="num_inference_steps" className="text-xl block mb-2">Number of Interence Steps</label>
                    <Slider id="num_inference_steps" name="num_inference_steps" minValue={1} maxValue={30} defaultValue={15} step={1} className="slider" />
                  </div>
                </>
                :
                selectedModel == "lambdalabs/sd-image-variations-diffusers" ?
                  <>
                    <div>
                      <label htmlFor="guidance" className="text-xl block mb-2">Guidance</label>
                      <Slider id="guidance" name="guidance" minValue={5} maxValue={15} defaultValue={8} step={1} className="slider" />
                    </div>
                  </>
                  :
                  <></>
            }

            <div>
              {
                submittingForm ?
                  <button type="button" className="block px-3 py-1 text-white rounded-sm bg-sky-900 text-center justify-content-center align-items-center" disabled>
                    <Spinner />
                  </button>
                  :
                  <button type="button" onClick={submitForm} className="block px-3 py-1 text-white rounded-sm bg-sky-700 hover:bg-sky-400">Submit</button>
              }
            </div>
          </div>
        </form>

        {
          result ?
            <div>
              <video controls preload="true" loop={true}>
                <source src={result} type={resultMimeType} />
              </video>
              <a href={result} download={resultFilename} className="block px-3 py-1 text-white rounded-sm bg-sky-700 hover:bg-sky-400">Download</a>
            </div>
            :
            <div className="text-center">
              Results will be shown here
            </div>
        }
      </div>
    </main>
  );
}
