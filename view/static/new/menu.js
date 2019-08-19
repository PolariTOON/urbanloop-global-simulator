import {state} from "./state.js";
const uploadButton = document.getElementById("upload-button").control;
const downloadButton = document.getElementById("download-button");
const createButton = document.getElementById("create-button").control;
const deleteButton = document.getElementById("delete-button").control;
const playButton = document.getElementById("play-button").control;
const pauseButton = document.getElementById("pause-button").control;
const accelerateButton = document.getElementById("accelerate-button").control;
const decelerateButton = document.getElementById("decelerate-button").control;
let timerDiv = document.getElementById('timer-div');
let speedDiv = document.getElementById('speed-div');

export function updateTimeFromJSON(timeJSON) {
    timerDiv.innerHTML = `Day ${timeJSON['day']}<br>${timeJSON['time']}`;
    speedDiv.innerHTML = timeJSON['speed'];

    if (timeJSON['decelerateJerky'] === 1) {
        if (!accelerateButton.classList.contains("btn-warning")) {
            accelerateButton.classList.remove("btn-light");
            accelerateButton.classList.add("btn-warning");
            accelerateButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!accelerateButton.classList.contains("btn-light")) {
            accelerateButton.classList.remove("btn-warning");
            accelerateButton.classList.add("btn-light");
            accelerateButton.removeAttribute("title");
        }
    }

    if (timeJSON['accelerateJerky'] === 1) {
        if (!decelerateButton.classList.contains("btn-warning")) {
            decelerateButton.classList.remove("btn-light");
            decelerateButton.classList.add("btn-warning");
            decelerateButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!decelerateButton.classList.contains("btn-light")) {
            decelerateButton.classList.remove("btn-warning");
            decelerateButton.classList.add("btn-light");
            decelerateButton.removeAttribute("title");
        }
    }
}

state.addEventListener("load", (event) => {
    uploadButton.disabled = true;
    downloadButton.download = `network-${state.networkIndex}.json`;
    downloadButton.href = `/networks/${state.networkIndex}/`;
    // createButton.disabled = true;
    deleteButton.disabled = false;
    playButton.disabled = true;
    pauseButton.disabled = true;
    // decelerateButton.disabled = false;
    // accelerateButton.disabled = false;
});

state.addEventListener("unload", (event) => {
    uploadButton.disabled = false;
    downloadButton.download = "";
    downloadButton.removeAttribute("href");
    // createButton.disabled = false;
    deleteButton.disabled = true;
    playButton.disabled = true;
    pauseButton.disabled = true;
    // decelerateButton.disabled = true;
    // accelerateButton.disabled = true;
});

state.addEventListener("play", (event) => {
    playButton.disabled = true;
    pauseButton.disabled = false;
});

state.addEventListener("pause", (event) => {
    playButton.disabled = false;
    pauseButton.disabled = true;
});

uploadButton.addEventListener("input", async (event) => {
    const {files} = uploadButton;
    if (files.length !== 1) {
        return;
    }
    try {
        const input = await new Response(files.item(0)).json(); // TODO: effectuer des contrôles sémantiques
        state.load(input);
    } catch {} // TODO
});

createButton.addEventListener("click", async (event) => {
    const input = null; // TODO
    state.load(input);
});

deleteButton.addEventListener("click", async (event) => {
    state.unload();
});

playButton.addEventListener("click", async (event) => {
    state.play();
});

pauseButton.addEventListener("click", async (event) => {
    state.pause();
});

decelerateButton.addEventListener("click", async (event) => {
    state.decelerate();
});

accelerateButton.addEventListener("click", async (event) => {
    state.accelerate();
});
