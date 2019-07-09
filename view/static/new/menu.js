import {changeNetworkButtonState} from "../tabs";
import {applyNetworkScene} from "../renderer";

let startButton = document.getElementById('start-button');
let stopButton = document.getElementById('stop-button');
let pauseButton = document.getElementById('pause-button');
let backwardButton = document.getElementById('backward-button');
let forwardButton = document.getElementById('forward-button');
let timerSpan = document.getElementById('timer-span');
let speedSpan = document.getElementById('speed-span');
let paused = false;
let running = false;

let configTab = document.getElementById("config-tab");
let interactTab = document.getElementById("interact-tab");

export function updateTimeFromJSON(timeJSON) {
    timerSpan.innerHTML = "Day " + timeJSON['day'] + "<br><br>" + timeJSON['time'];
    speedSpan.innerHTML = timeJSON['speed'];

    if (timeJSON['decelerateJerky'] === 1) {
        if (!backwardButton.classList.contains("btn-warning")) {
            backwardButton.classList.remove("btn-light");
            backwardButton.classList.add("btn-warning");
            backwardButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!backwardButton.classList.contains("btn-light")) {
            backwardButton.classList.remove("btn-warning");
            backwardButton.classList.add("btn-light");
            backwardButton.removeAttribute("title");
        }
    }

    if (timeJSON['accelerateJerky'] === 1) {
        if (!forwardButton.classList.contains("btn-warning")) {
            forwardButton.classList.remove("btn-light");
            forwardButton.classList.add("btn-warning");
            forwardButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!forwardButton.classList.contains("btn-light")) {
            forwardButton.classList.remove("btn-warning");
            forwardButton.classList.add("btn-light");
            forwardButton.removeAttribute("title");
        }
    }
}

pauseButton.disabled = true;
backwardButton.disabled = true;
forwardButton.disabled = true;

startButton.onclick = async () => {
    if (running) return;
    pauseButton.disabled = false;
    backwardButton.disabled = false;
    forwardButton.disabled = false;
    saveConfigButton.disabled = true;
    resetConfigButton.disabled = true;
    networkSelection.disabled = true;
    changeNetworkButtonState(true);
    startButton.classList.add('not-shown');
    stopButton.classList.remove('not-shown');
    await fetch('/clock/start/', { //TODO : requête start
        method: "POST"
    });
    running = true;
};

stopButton.onclick = async () => {
    if (!running) return;
    pauseButton.disabled = true;
    backwardButton.disabled = true;
    forwardButton.disabled = true;
    saveConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    networkSelection.disabled = false;
    changeNetworkButtonState(false);
    stopButton.classList.add('not-shown');
    running = false;
    await fetch('/clock/stop/', { //TODO : requête stop
        method: "POST"
    });
    document.getElementById('timer-span').innerHTML = "Day -<br><br>--:--:--";
    applyNetworkScene();
};

pauseButton.onclick = () => {
    if (paused) {
        fetch('/clock/resume/', { //TODO : requête resume
            method: "POST"
        });
        pauseButton.innerHTML = "Pause";
        paused = false;
    } else {
        fetch('/clock/pause/', { //TODO : requête pause
            method: "POST"
        });
        pauseButton.innerHTML = "Resume";
        paused = true;
    }
};

backwardButton.onclick = () => {
    if (!running) return;
    fetch('/clock/decelerate/', { //TODO : requête decelerate
        method: "POST"
    });
};

forwardButton.onclick = () => {
    if (!running) return;
    fetch('/clock/accelerate/', { //TODO : requête accelerate
        method: "POST"
    });
};