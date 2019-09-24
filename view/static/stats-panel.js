import {state} from "./state.js";

const statsTab = document.getElementById("stats-content");
const notImplemented = document.createElement("p");
notImplemented.append("Not implemented");

state.addEventListener("update", (event) => {
    statsTab.append(notImplemented);
});
