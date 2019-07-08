let startButton = document.getElementById('start-button');
let backwardButton = document.getElementById('backward-button');
let forwardButton = document.getElementById('forward-button');
let timerSpan = document.getElementById('timer-span');
let speedSpan = document.getElementById('speed-span');

let configTab = document.getElementById("config-tab");
let interactTab = document.getElementById("interact-tab");

function updateTimeFromJSON(timeJSON) {
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