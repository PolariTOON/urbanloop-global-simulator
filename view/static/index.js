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
// mise à jour de l'affichage du réseau toutes les 100ms -> pas forcément nécessaire ? on dirait que l'affichage est déjà continu au début de la simulation (ça bloque après un bug)
let delay = 100
console.log("Foo")
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
