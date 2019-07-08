import {applyNetworkScene} from "./network.js";

let networkSelection = document.getElementById('conf-topology-0');
let networkErrorText = document.getElementById('network-error-text');
let refillCheckBox = document.getElementById('conf-capsule-2');
let fulfillPeriod = document.getElementById('conf-capsule-3');
let endlessCheckBox = document.getElementById('conf-simulation-1');
let duration = document.getElementById('conf-simulation-2');

refillCheckBox.onclick = () => {
    fulfillPeriod.disabled = !refillCheckBox.checked;
};

networkSelection.onchange = () => {
    networkErrorText.innerHTML = "Select, add, remove or download a network JSON file";
    networkErrorText.classList.remove('form-text-error');
    networkErrorText.classList.add('text-muted');

    let selectedName = networkSelection[networkSelection.selectedIndex].value;
    applyNetworkScene(selectedName)
};

endlessCheckBox.onclick = () => {
    duration.disabled = endlessCheckBox.checked;
};

export async function updateConfigPanel() {
    const configJSON = await (await fetch('/config/')).json();
    document.getElementById('conf-travelers-0').value = configJSON['travelers_per_day'];
    document.getElementById('conf-travelers-1').value = configJSON['trip_limit'];
    document.getElementById('conf-travelers-2').value = configJSON['traveler_limit'];
    document.getElementById('conf-travelers-3').value = configJSON['ascent_descent_duration'];
    document.getElementById('conf-travelers-4').value = configJSON['morning_peak_hour'];
    document.getElementById('conf-travelers-5').value = configJSON['evening_peak_hour'];

    document.getElementById('conf-probabilities-0').value = configJSON['activity_and_residential_percent'];
    document.getElementById('conf-probabilities-1').value = configJSON['city_percent'];
    document.getElementById('conf-probabilities-2').value = configJSON['activity_and_residential_fluctuation'];

    document.getElementById('conf-capsule-0').value = configJSON['max_speed'];
    document.getElementById('conf-capsule-1').value = configJSON['number_of_capsules'];
    document.getElementById('conf-capsule-2').checked = ['true', 'True'].includes(configJSON['station_refill']);
    document.getElementById('conf-capsule-3').value = configJSON['fulfill_period'];

    document.getElementById('conf-routing-0').value = configJSON['switched_cost'];
    document.getElementById('conf-routing-1').value = configJSON['my_timer'];
    document.getElementById('conf-routing-2').value = configJSON['timer_other'];

    document.getElementById('conf-simulation-0').checked = ['true', 'True'].includes(configJSON['real_time']);
    document.getElementById('conf-simulation-1').checked = ['true', 'True'].includes(configJSON['endless']);
    document.getElementById('conf-simulation-2').value = configJSON['duration'];
    document.getElementById('conf-simulation-3').value = configJSON['start_hour'];
    document.getElementById('conf-simulation-4').checked = ['true', 'True'].includes(configJSON['logs']);

    duration.disabled = ['true', 'True'].includes(configJSON['endless']);
    fulfillPeriod.disabled = ['false, False'].includes(configJSON['station_refill']);

    updateNetworkSelection();
}

async function updateNetworkSelection() {
    while (networkSelection.firstChild) {
        networkSelection.removeChild(networkSelection.firstChild);
    }
    const listNetworkFileNameJSON = await (await fetch('/networks/')).json();
    for (const networkFileNameJSON of listNetworkFileNameJSON) {
        let option = document.createElement('option');
        option.innerHTML = networkFileNameJSON['fileName'];
        networkSelection.appendChild(option);
    }
}
