import {state} from "./state.js";
import "./menu.js";
import "./network.js";

let requestAnimationFrameId = 0;

state.addEventListener("play", async (event) => {
    if (requestAnimationFrameId !== 0) {
        return;
    }
    requestAnimationFrameId = requestAnimationFrame(() => {
        state.update();
        requestAnimationFrameId = 0;
    });
});

state.addEventListener("pause", async (event) => {
    if (requestAnimationFrameId === 0) {
        return;
    }
    cancelAnimationFrame(requestAnimationFrameId);
    requestAnimationFrameId = 0;
});

state.addEventListener("update", async (event) => {
    if (requestAnimationFrameId !== 0) {
        return;
    }
    requestAnimationFrameId = requestAnimationFrame(() => {
        state.update();
        requestAnimationFrameId = 0;
    });
});

state.reload();

// TODO: ajouter un timeout pour diminuer la fréquence de rafraichissement
