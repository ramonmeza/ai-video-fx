"use client";

import React, { useState, useEffect } from 'react';

const API_URL = "http://localhost:8000"

export default function Home() {
  const [models, setModels] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/models`)
      .then(response => response.json())
      .then(json => setModels(json['models']))
      .catch(error => console.error(error));
  }, []);

  function updateFilename(event) {
    const filename = document.getElementById("FileInput").value;
    document.getElementById("filename").innerHTML = filename;
  }

  return (
    <main>
      <div className="container mx-auto">
        <form className="space-y-2">
          <div>
            <label type="button" htmlFor="FileInput" className="inline px-3 py-1 text-white rounded-sm bg-sky-700 hover:bg-sky-400">Select Video</label>
            <span id="filename"></span>
            <input type="file" id="FileInput" name="file_input" className="hidden" onChange={updateFilename}></input>
          </div>

          <div>
            <label htmlFor="ModelInput" className="inline">Select a model: </label>
            <select className="form-select inline" id="ModelInput" name="model_input">
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

          <button type="button" className="block px-3 py-1 text-white rounded-sm bg-sky-700 hover:bg-sky-400">Submit</button>
        </form>
      </div>
    </main>
  );
}
