let playPauseButton = document.getElementById('play-pause-button');
let accelerateButton = document.getElementById('accelerate-button');
let decelerateButton = document.getElementById('decelerate-button');
let timerDiv = document.getElementById('timer-div');
let speedDiv = document.getElementById('speed-div');
let running = false;

export function updateTimeFromJSON(timeJSON) {
    timerDiv.innerHTML = `Day ${timeJSON['day']}<br>${timeJSON['time']}`;
    speedDiv.innerHTML = timeJSON['speed'];

    if (timeJSON['decelerateJerky'] === 1) {
        if (!accelerateButton.classList.contains("btn-warning")) {
            accelerateButton.classList.remove("btn-light");
            accelerateButton.classList.add("btn-warning");
            accelerateButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!accelerateButton.classList.contains("btn-light")) {
            accelerateButton.classList.remove("btn-warning");
            accelerateButton.classList.add("btn-light");
            accelerateButton.removeAttribute("title");
        }
    }

    if (timeJSON['accelerateJerky'] === 1) {
        if (!decelerateButton.classList.contains("btn-warning")) {
            decelerateButton.classList.remove("btn-light");
            decelerateButton.classList.add("btn-warning");
            decelerateButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!decelerateButton.classList.contains("btn-light")) {
            decelerateButton.classList.remove("btn-warning");
            decelerateButton.classList.add("btn-light");
            decelerateButton.removeAttribute("title");
        }
    }
}

accelerateButton.disabled = true;
decelerateButton.disabled = true;

playPauseButton.addEventListener("click", () => {
    if (!running) {
        fetch('/networks/0/clock/play/', { //TODO : requête play
            method: "POST"
        });
        playPauseButton.innerHTML = "Pause";
    } else {
        fetch('/networks/0/clock/pause/', { //TODO : requête pause
            method: "POST"
        });
        playPauseButton.innerHTML = "Play";
    }
    running = !running
});

accelerateButton.addEventListener("click", () => {
    if (!running) return;
    fetch('/clock/decelerate/', { //TODO : requête decelerate
        method: "POST"
    });
});

decelerateButton.addEventListener("click", () => {
    if (!running) return;
    fetch('/clock/accelerate/', { //TODO : requête accelerate
        method: "POST"
    });
});
