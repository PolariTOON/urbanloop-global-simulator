import {state} from "./state.js";
import {Statisctics} from "./statisctics.js";

const statsTab = document.getElementById("stats-content");
const notImplemented = document.createElement("p");
notImplemented.append("Not implemented");

function serialize() {
	const stats = `
	<dl>
	<dt>
        <button class="link">Number of traverlers:</button>
    </dt>
	<dd>${state.stats.nbTraveler}</dd>
	</dl>
` 
statsTab.innerHTML = stats;
}

state.addEventListener("update", (event) => {
    //statsTab.append(notImplemented);
	serialize();
});
