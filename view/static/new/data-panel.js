// Ce fichier gère le panneau d'affichage de l'objet sélectionné

import {state} from "./state.js";
import {Loop} from "./loop.js";
import {Switch} from "./switch.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Pod} from "./pod.js";
import {Sensor} from "./sensor.js";

let dataTab = document.getElementById("data-tab");

state.addEventListener("update", async (event) => {
    let data = "";
    if (state.selectedEntity instanceof Loop) {
        data += `<p>Loop: ${state.selectedEntity.json["name"]}</p>`;
        data += `<p>Circumference: ${state.selectedEntity.json["size"]}</p>`;
        data += `<p>Center coordinates: [${state.selectedEntity.json["x"]};${state.selectedEntity.json["y"]}]</p>`;
        data += `<p>Clockwise: ${state.selectedEntity.json["clockwise"]}</p>`;
        data += "<p>Elements: ";
        let elements = state.selectedEntity.json["objects"];
        for (const key in elements) {
            data += `<br>&nbsp;${elements[key]}`;
        }
        data += "</p>";
    } else if (state.selectedEntity instanceof Switch) {
        data += `<p>Switch n°${state.selectedEntity.json["id"]}</p>`;
        data += `<p>Loop of the switch: ${state.selectedEntity.json["my_loop_name"]}</p>`;
        data += `<p>&nbsp; Next element : ${state.selectedEntity.json["next_element_name"]}</p>`;
        data += `<p>Loop switched: ${state.selectedEntity.json["other_loop_name"]}</p>`;
        data += `<p>&nbsp; Next element: ${state.selectedEntity.json["next_other_element_name"]}</p>`;
        data += `<p>Size of the link: ${state.selectedEntity.json["size"]}</p>`;
    } else if (state.selectedEntity instanceof Station) {
        data += `<p>Station: ${state.selectedEntity.json["name"]}</p>`;
        data += `<p>Station Type: ${state.selectedEntity.json["type"]}</p>`;
        data += `<p>Loop: ${state.selectedEntity.json["outerCircle"]}</p>`;
        data += `<p>Capacity: ${state.selectedEntity.json["capacity"]}</p>`;
        data += `<p>Next element: ${state.selectedEntity.json["next_element"]}</p>`;
        data += `<p>Waiting travelers: ${state.selectedEntity.json["nb_travelers"]}</p>`;
        data += `<p>Capsules: ${state.selectedEntity.json["nb_capsules"]}`;
        for (const k in state.selectedEntity.json["capsules"]) {
            data += `<br>&nbsp;Capsule #${state.selectedEntity.json["capsules"][k]}`;
        }
        data += "</p>";
    } else if (state.selectedEntity instanceof Shed) {
        data += `<p>Warehouse n°${state.selectedEntity.json["id"]}</p>`;
        data += `<p>Loop: ${state.selectedEntity.json["outerCircle"]}</p>`;
        data += `<p>Capacity: ${state.selectedEntity.json["capacity"]}</p>`;
        data += `<p>Next element: ${state.selectedEntity.json["next_element"]}</p>`;
        data += `<p>Capsules: ${state.selectedEntity.json["nb_capsules"]}`;
        data += "</p>";
    } else if (state.selectedEntity instanceof Pod) {
        data += `<p>Capsule n°${state.selectedEntity.json["id"]}</p>`;
        data += `<p>Contains a traveler: ${state.selectedEntity.json["travelerNumber"] !== 0}</p>`;
        let destination = state.selectedEntity.json["destination"] === undefined ? "None" : state.selectedEntity.json["destination"];
        data += "<p>Destination: " + destination + "</p>";
        data += `<p>Current Loop: ${state.selectedEntity.json["outerCircle"]}</p>`;
        data += `<p>Last or current element: ${state.selectedEntity.json["current_element"]}</p>`;
        data += `<p>Next element: ${state.selectedEntity.json["next_element"]}</p>`;
    } else if (state.selectedEntity instanceof Sensor) {
        data += `<p>Sensor n°${state.selectedEntity.json["id"]}</p>`
    }
    else {
        data += "<p>Nothing selected.</p>";
    }
    dataTab.innerHTML = data;
});
