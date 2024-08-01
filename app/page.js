"use client";

import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:8000"

export default function Home() {
  const [models, setModels] = useState(null);
  const [submittingForm, setSubmittingForm] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/models`)
      .then(response => response.json())
      .then(json => setModels(json["models"]))
      .catch(error => console.error(error));
  }, []);

  function updateFilename(event) {
    const filename = document.getElementById("FileInput").value;
    document.getElementById("filename").innerHTML = filename;
  }

  async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById("UploadForm");
    const formData = new FormData(form);
    setSubmittingForm(true);
    const response = await fetch(`${API_URL}/generate?model=${formData.get("model")}`, {
      method: "POST",
      body: formData
    });
    console.log(response);
    setSubmittingForm(false);
  }

  return (
    <main>
      <div className="container mx-auto">
        <form id="UploadForm" className="space-y-2" method="POST" encType="multipart/form-data">
          <div>
            <label type="button" htmlFor="FileInput" className="inline px-3 py-1 text-white rounded-sm bg-sky-700 hover:bg-sky-400">Select Video</label>
            <span id="filename"></span>
            <input type="file" id="FileInput" name="file" className="hidden" onChange={updateFilename} accept="video/*"></input>
          </div>

          <div>
            <label htmlFor="ModelInput" className="inline">Select a model: </label>
            <select className="form-select inline" id="ModelInput" name="model">
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
            submittingForm ?
              <button type="button" className="block px-3 py-1 text-white rounded-sm bg-sky-900 text-center justify-content-center align-items-center" disabled>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="black" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
              :
              <button type="button" onClick={submitForm} className="block px-3 py-1 text-white rounded-sm bg-sky-700 hover:bg-sky-400">Submit</button>
          }
        </form>
      </div>
    </main>
  );
}
