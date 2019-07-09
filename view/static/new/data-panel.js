// Ce fichier gère le panneau d'affichage de l'objet sélectionné

import {appState} from "./network.js";
import {Loop} from "./loop.js";
import {Switch} from "./switch.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Pod} from "./pod.js";
import {Sensor} from "./sensor.js";

let dataTab = document.getElementById("data-tab");

export function updateDataPanel() {
    let data = "";
    if (appState.selectedObject instanceof Loop) {
        data += `<p>Loop: ${appState.selectedObject.json["name"]}</p>`;
        data += `<p>Circumference: ${appState.selectedObject.json["size"]}</p>`;
        data += `<p>Center coordinates: [${appState.selectedObject.json["x"]};${appState.selectedObject.json["y"]}]</p>`;
        data += `<p>Clockwise: ${appState.selectedObject.json["clockwise"]}</p>`;
        data += "<p>Elements: ";
        let elements = appState.selectedObject.json["objects"];
        for (const key in elements) {
            data += `<br>&nbsp;${elements[key]}`;
        }
        data += "</p>";
    } else if (appState.selectedObject instanceof Switch) {
        data += `<p>Switch n°${appState.selectedObject.json["id"]}</p>`;
        data += `<p>Loop of the switch: ${appState.selectedObject.json["my_loop_name"]}</p>`;
        data += `<p>&nbsp; Next element : ${appState.selectedObject.json["next_element_name"]}</p>`;
        data += `<p>Loop switched: ${appState.selectedObject.json["other_loop_name"]}</p>`;
        data += `<p>&nbsp; Next element: ${appState.selectedObject.json["next_other_element_name"]}</p>`;
        data += `<p>Size of the link: ${appState.selectedObject.json["size"]}</p>`;
    } else if (appState.selectedObject instanceof Station) {
        data += `<p>Station: ${appState.selectedObject.json["name"]}</p>`;
        data += `<p>Station Type: ${appState.selectedObject.json["type"]}</p>`;
        data += `<p>Loop: ${appState.selectedObject.json["outerCircle"]}</p>`;
        data += `<p>Capacity: ${appState.selectedObject.json["capacity"]}</p>`;
        data += `<p>Next element: ${appState.selectedObject.json["next_element"]}</p>`;
        data += `<p>Waiting travelers: ${appState.selectedObject.json["nb_travelers"]}</p>`;
        data += `<p>Capsules: ${appState.selectedObject.json["nb_capsules"]}`;
        for (const k in appState.selectedObject.json["capsules"]) {
            data += `<br>&nbsp;Capsule #${appState.selectedObject.json["capsules"][k]}`;
        }
        data += "</p>";
    } else if (appState.selectedObject instanceof Shed) {
        data += `<p>Warehouse n°${appState.selectedObject.json["id"]}</p>`;
        data += `<p>Loop: ${appState.selectedObject.json["outerCircle"]}</p>`;
        data += `<p>Capacity: ${appState.selectedObject.json["capacity"]}</p>`;
        data += `<p>Next element: ${appState.selectedObject.json["next_element"]}</p>`;
        data += `<p>Capsules: ${appState.selectedObject.json["nb_capsules"]}`;
        data += "</p>";
    } else if (appState.selectedObject instanceof Pod) {
        data += `<p>Capsule n°${appState.selectedObject.json["id"]}</p>`;
        data += `<p>Contains a traveler: ${appState.selectedObject.json["travelerNumber"] !== 0}</p>`;
        let destination = appState.selectedObject.json["destination"] === undefined ? "None" : appState.selectedObject.json["destination"];
        data += "<p>Destination: " + destination + "</p>";
        data += `<p>Current Loop: ${appState.selectedObject.json["outerCircle"]}</p>`;
        data += `<p>Last or current element: ${appState.selectedObject.json["current_element"]}</p>`;
        data += `<p>Next element: ${appState.selectedObject.json["next_element"]}</p>`;
    } else if (appState.selectedObject instanceof Sensor) {
        data += `<p>Sensor n°${appState.selectedObject.json["id"]}</p>`
    }
    else {
        data += "<p>Nothing selected.</p>";
    }
    dataTab.innerHTML = data;
}

