import {state} from "./state.js";
const uploadButton = document.getElementById("upload-button").control;
const downloadButton = document.getElementById("download-button");
const createButton = document.getElementById("create-button").control;
const deleteButton = document.getElementById("delete-button").control;
const playButton = document.getElementById("play-button").control;
const pauseButton = document.getElementById("pause-button").control;
const accelerateButton = document.getElementById("accelerate-button").control;
const decelerateButton = document.getElementById("decelerate-button").control;
const dataTab = document.getElementById("data-tab").control;
const statsTab = document.getElementById("stats-tab").control;
const viewsTab = document.getElementById("views-tab").control;

state.addEventListener("load", (event) => {
    uploadButton.disabled = true;
    downloadButton.download = `network-${state.networkIndex}.json`;
    downloadButton.href = `/networks/${state.networkIndex}/`;
    // createButton.disabled = true;
    deleteButton.disabled = false;
    playButton.disabled = false;
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

let currentPanel = null;
for (const tab of [dataTab, statsTab, viewsTab]) {
    tab.addEventListener("click", async (event) => {
        if (!tab.checked) {
            return;
        }
        const oldPanel = currentPanel;
        const newPanel = document.getElementById(tab.value);
        if (oldPanel !== null) {
            oldPanel.hidden = true;
        }
        if (newPanel === null || newPanel === oldPanel) {
            tab.checked = false;
            currentPanel = null;
            state.resize();
            return;
        }
        newPanel.hidden = false;
        currentPanel = newPanel;
        if (oldPanel === null) {
            state.resize();
        }
    });
    if (tab.checked) {
        tab.click();
    } else {
        const panel = document.getElementById(tab.value);
        panel.hidden = true;
    }
}
if (currentPanel !== null) {
    state.resize();
}
