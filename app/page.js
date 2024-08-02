"use client";

import React, { useState, useEffect } from "react";
import Spinner from "./spinner";

const API_URL = "http://localhost:8000"

export default function Home() {
  const [models, setModels] = useState(null);
  const [result, setResult] = useState(null);
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

    const response = await fetch(`${API_URL}/generate?model=${formData.get("model")}`, {
      method: "POST",
      body: formData
    }).catch(error => console.error(error));

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "temp.avi";
      document.body.appendChild(a);
      a.click(); //autodownloads
      a.remove();
      window.URL.revokeObjectURL(url);
    } else {
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
              <select className="form-select min-w-full" id="model" name="model">
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
              <video>
                <source src="" />
              </video>
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
