import {state} from "./state.js";
import {Pod} from "./pod.js";
import {Section} from "./section.js";
import {Sensor} from "./sensor.js";
import {Shed} from "./shed.js";
import {Station} from "./station.js";
import {Switch} from "./switch.js";

const dataTab = document.getElementById("data-content");
const closeButton = document.getElementById("close-button").control;


function serialize() {
    const data = `\
${state.selectedEntity !== null ? `\
<dl>
    <dt>Type</dt>
    <dd>${state.selectedEntity.constructor.name}</dd>
    <dt>Name</dt>
    <dd>${state.selectedEntity._name}</dd>
    <dt>Coordinates (in m)</dt>
    <dd>${state.selectedEntity._x}, ${state.selectedEntity._y}</dd>
${state.selectedEntity instanceof Pod ? `\
    <dt>Position (in m)</dt>
    <dd>${state.selectedEntity._position}</dd>
    <dt>Speed (in m / s)</dt>
    <dd>${state.selectedEntity._speed}</dd>
    <dt>Source</dt>
    <dd>${state.selectedEntity._source}</dd>
    <dt>Destination</dt>
    <dd>${state.selectedEntity._destination}</dd>
    <dt>Travelers</dt>
    <dd>${state.selectedEntity._travelerCount} / ${state.selectedEntity._travelerMax}</dd>
` : state.selectedEntity instanceof Section ? `\
    <dt>Speed (in m / s)</dt>
    <dd>${state.selectedEntity._speed}</dd>
    <dt>Length (in m)</dt>
    <dd>${state.selectedEntity._length}</dd>
` : state.selectedEntity instanceof Sensor ? `\
` : state.selectedEntity instanceof Shed ? `\
    <dt>Pods</dt>
    <dd>${state.selectedEntity._podCount} / ${state.selectedEntity._podMax}</dd>
` : state.selectedEntity instanceof Station ? `\
    <dt>Station type</dt>
    <dd>${state.selectedEntity._stationType}</dd><!-- TODO: remplacer par quelque chose d'explicite -->
    <dt>Pods</dt>
    <dd>${state.selectedEntity._podCount} / ${state.selectedEntity._podMax}</dd>
    <dt>Travelers</dt>
    <dd>${state.selectedEntity._travelerCount} (${state.selectedEntity._travelerAllTimeCount} since simulation start)</dd>
		<dt>Boarding Travelers</dt>
		<dd>${state.selectedEntity._travelerBoarding}</dd>
    <dt>Average waiting duration (in s)</dt>
    <dd>${state.selectedEntity._travelerAverageWaitingTime}</dd>
` : state.selectedEntity instanceof Switch ? `\
    <dt>Speed (in m / s)</dt>
    <dd>${state.selectedEntity._speed}</dd>
    <dt>Length (in m)</dt>
    <dd>${state.selectedEntity._length}</dd>
` : `\
`}
</dl>
` : `\
<p>Nothing selected</p>
`}`;
    dataTab.innerHTML = data;
}

state.addEventListener("update", (event) => {
    serialize();
});

state.addEventListener("close", (event) => {
    serialize();
});

closeButton.addEventListener("click", async (event) => {
    if (closeButton["value"].localeCompare("Close section") == 0){
        console.log("a")
        closeButton["value"] = "Open section";
    }
    else {
        console.log("b")
        closeButton["value"] = "Close section";
    }
    state.close();
});

closeButton.style.display = "none";
closeButton.disabled = false;

// state.addEventListener("select", (event) => {
//     serialize();
// });
