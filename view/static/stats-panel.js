import {state} from "./state.js";
import {Statisctics} from "./statisctics.js";

const statsTab = document.getElementById("stats-content");
const notImplemented = document.createElement("p");
notImplemented.append("Not implemented");

function serialize() {
	const stats = `
    <script>
        serie1(){
            }
    </script>
	<dl>

	<dt>
        <button class="link"; onclick="serie1()">Number of traveler:</button>
    </dt>
	<dd>${state.stats.nbTraveler}</dd>

    <dt>
        <button class="link">Average waiting time:</button>
    </dt>
    <dd>${state.stats.waitingTime} s</dd>

    <dt>
        <button class="link">Number of traveling pods:</button>
    </dt>
    <dd>${state.stats.nbPod}</dd>

	</dl>
` 
statsTab.innerHTML = stats;
}

state.addEventListener("update", (event) => {
    //statsTab.append(notImplemented);
	serialize();
});
