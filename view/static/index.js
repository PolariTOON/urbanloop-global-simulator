import {state} from "./state.js";
import "./menu.js";
import "./network.js";
import "./data-panel.js";
import "./stats-panel.js"
import "./views-panel.js"

let requestAnimationFrameId = 0;

state.addEventListener("play", (event) => {
    if (requestAnimationFrameId !== 0) {
        return;
    }
    requestAnimationFrameId = requestAnimationFrame(() => {
        state.update();
        requestAnimationFrameId = 0;
    });
});

state.addEventListener("pause", (event) => {
    if (requestAnimationFrameId === 0) {
        return;
    }
    cancelAnimationFrame(requestAnimationFrameId);
    requestAnimationFrameId = 0;
});

state.addEventListener("update", (event) => {
    if (requestAnimationFrameId !== 0) {
        return;
    }
    requestAnimationFrameId = requestAnimationFrame(() => {
        state.update();
        requestAnimationFrameId = 0;
    });
});

/*
// if we want to increase framerate
let delay = 100
setInterval(function(){
    if (requestAnimationFrameId !== 0) {
        return;
    }
    requestAnimationFrameId = requestAnimationFrame(() => {
        state.update();
        requestAnimationFrameId = 0;
    });
}, delay);
*/

state.reload();
