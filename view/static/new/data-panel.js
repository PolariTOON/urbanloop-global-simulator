// Ce fichier gère le panneau d'affichage de l'objet sélectionné

import {state} from "./state.js";
import {Loop} from "./loop.js";
import {Switch} from "./switch.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Pod} from "./pod.js";
import {Sensor} from "./sensor.js";

let dataTab = document.getElementById("data-tab");

export function updateDataPanel() {
    let data = "";
    if (state.selectedObject instanceof Loop) {
        data += `<p>Loop: ${state.selectedObject.json["name"]}</p>`;
        data += `<p>Circumference: ${state.selectedObject.json["size"]}</p>`;
        data += `<p>Center coordinates: [${state.selectedObject.json["x"]};${state.selectedObject.json["y"]}]</p>`;
        data += `<p>Clockwise: ${state.selectedObject.json["clockwise"]}</p>`;
        data += "<p>Elements: ";
        let elements = state.selectedObject.json["objects"];
        for (const key in elements) {
            data += `<br>&nbsp;${elements[key]}`;
        }
        data += "</p>";
    } else if (state.selectedObject instanceof Switch) {
        data += `<p>Switch n°${state.selectedObject.json["id"]}</p>`;
        data += `<p>Loop of the switch: ${state.selectedObject.json["my_loop_name"]}</p>`;
        data += `<p>&nbsp; Next element : ${state.selectedObject.json["next_element_name"]}</p>`;
        data += `<p>Loop switched: ${state.selectedObject.json["other_loop_name"]}</p>`;
        data += `<p>&nbsp; Next element: ${state.selectedObject.json["next_other_element_name"]}</p>`;
        data += `<p>Size of the link: ${state.selectedObject.json["size"]}</p>`;
    } else if (state.selectedObject instanceof Station) {
        data += `<p>Station: ${state.selectedObject.json["name"]}</p>`;
        data += `<p>Station Type: ${state.selectedObject.json["type"]}</p>`;
        data += `<p>Loop: ${state.selectedObject.json["outerCircle"]}</p>`;
        data += `<p>Capacity: ${state.selectedObject.json["capacity"]}</p>`;
        data += `<p>Next element: ${state.selectedObject.json["next_element"]}</p>`;
        data += `<p>Waiting travelers: ${state.selectedObject.json["nb_travelers"]}</p>`;
        data += `<p>Capsules: ${state.selectedObject.json["nb_capsules"]}`;
        for (const k in state.selectedObject.json["capsules"]) {
            data += `<br>&nbsp;Capsule #${state.selectedObject.json["capsules"][k]}`;
        }
        data += "</p>";
    } else if (state.selectedObject instanceof Shed) {
        data += `<p>Warehouse n°${state.selectedObject.json["id"]}</p>`;
        data += `<p>Loop: ${state.selectedObject.json["outerCircle"]}</p>`;
        data += `<p>Capacity: ${state.selectedObject.json["capacity"]}</p>`;
        data += `<p>Next element: ${state.selectedObject.json["next_element"]}</p>`;
        data += `<p>Capsules: ${state.selectedObject.json["nb_capsules"]}`;
        data += "</p>";
    } else if (state.selectedObject instanceof Pod) {
        data += `<p>Capsule n°${state.selectedObject.json["id"]}</p>`;
        data += `<p>Contains a traveler: ${state.selectedObject.json["travelerNumber"] !== 0}</p>`;
        let destination = state.selectedObject.json["destination"] === undefined ? "None" : state.selectedObject.json["destination"];
        data += "<p>Destination: " + destination + "</p>";
        data += `<p>Current Loop: ${state.selectedObject.json["outerCircle"]}</p>`;
        data += `<p>Last or current element: ${state.selectedObject.json["current_element"]}</p>`;
        data += `<p>Next element: ${state.selectedObject.json["next_element"]}</p>`;
    } else if (state.selectedObject instanceof Sensor) {
        data += `<p>Sensor n°${state.selectedObject.json["id"]}</p>`
    }
    else {
        data += "<p>Nothing selected.</p>";
    }
    dataTab.innerHTML = data;
}
