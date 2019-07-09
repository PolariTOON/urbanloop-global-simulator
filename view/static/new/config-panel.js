import {applyNetworkScene, getDefaultFilename} from "./network.js";
import {fetchTimeout} from "./main-page";

export let networkSelection = document.getElementById('conf-topology-0');
export let saveConfigButton = document.getElementById('config-save-button');
export let resetConfigButton = document.getElementById('config-reset-button');

let networkErrorText = document.getElementById('network-error-text');
let refillCheckBox = document.getElementById('conf-capsule-2');
let fulfillPeriod = document.getElementById('conf-capsule-3');
let endlessCheckBox = document.getElementById('conf-simulation-1');
let duration = document.getElementById('conf-simulation-2');
let networkAddButton = document.getElementById('network-add-btn');
let networkDlButton = document.getElementById('network-dl-btn');
let networkFavButton = document.getElementById('network-fav-btn');
let networkRemoveButton = document.getElementById('network-remove-btn');
let networkText = document.getElementById('network-text');
let networkFileInput = document.getElementById('conf-topology-1');

function resetNetworkErrorText() {
    networkErrorText.innerHTML = "Select, add, remove or download a network JSON file";
    networkErrorText.classList.remove('form-text-error');
    networkErrorText.classList.add('text-muted');
}

export function changeNetworkButtonState(disabled = false) {
    networkAddButton.disabled = disabled;
    networkDlButton.disabled = disabled;
    networkFavButton.disabled = disabled;
    networkRemoveButton.disabled = disabled;
}

export async function updateConfigPanel() {
    const configJSON = await (await fetch('/config/')).json(); //TODO : requête config
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
    const listNetworkFileNameJSON = await (await fetch('/networks/')).json(); //TODO : requête networks
    for (const networkFileNameJSON of listNetworkFileNameJSON) {
        let option = document.createElement('option');
        option.innerHTML = networkFileNameJSON['fileName'];
        networkSelection.appendChild(option);
    }
}


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

networkFileInput.onchange = () => {
    let value = networkFileInput.value;
    let extension = value.substr(value.lastIndexOf('.') + 1).toLowerCase();

    if (extension !== 'json') {
        networkErrorText.innerHTML = "Network file extension must be .json";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
        return;
    }

    resetNetworkErrorText();
    changeNetworkButtonState(true);

    let name;
    if (value.includes('/')) {
        let slashSplit = value.split('/');
        name = slashSplit[slashSplit.length - 1]
    } else {
        let backslashSplit = value.split('\\');
        name = backslashSplit[backslashSplit.length - 1]
    }

    let reader = new FileReader();
    reader.readAsText(networkFileInput.files[0], "UTF-8");
    reader.onload = async (event) => {
        let isValidJSON = true;
        let parsedJSON;

        try {
            parsedJSON = JSON.parse(event.target.result);
        } catch (error) {
            isValidJSON = false;
        }

        // In the future, isValidJSON should be false if the uploaded file doesn't respect network syntax
        if (!isValidJSON) {
            networkErrorText.innerHTML = "The uploaded JSON file isn't valid";
            networkErrorText.classList.remove('text-muted');
            networkErrorText.classList.add('form-text-error');
            changeNetworkButtonState(false);
            return;
        }

        await fetchTimeout(1000, '/' + name + '/add/', { //TODO : requête add
            method: 'POST',
            body: JSON.stringify(parsedJSON)
        });
        networkAddButton.title = "Network file has been added !";
        setTimeout(() => {
            networkAddButton.removeAttribute("title");
        }, 3000);
    };

    reader.onerror = () => {
        networkErrorText.innerHTML = "An error occurred while loading file";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
    };
};

networkAddButton.onclick = () => {
    document.getElementById('conf-topology-1').dispatchEvent(new CustomEvent('click'));
};

networkAddButton.onmouseenter = () => {
    networkText.innerHTML = "Add network json file"
};

networkAddButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

networkRemoveButton.onclick = async () => {
    let selectedName = networkSelection[networkSelection.selectedIndex].value;

    if (selectedName === getDefaultFilename()) {
        networkErrorText.innerHTML = "Cannot remove default file";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
        return;
    }

    resetNetworkErrorText();
    changeNetworkButtonState(true);

    await fetchTimeout(1000, '/' + selectedName + '/remove/', { // TODO : requête remove
        method: "POST"
    });
    document.getElementById('conf-topology-0').dispatchEvent(new CustomEvent('change'));
    networkRemoveButton.title = "Selected network has been removed !";
    setTimeout(() => {
        networkRemoveButton.removeAttribute("title");
    }, 3000);
};

networkRemoveButton.onmouseenter = () => {
    networkText.innerHTML = "Remove selected network from the list"
};

networkRemoveButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

networkDlButton.onclick = async () => {
    let selectedName = networkSelection[networkSelection.selectedIndex].value;
    const networkJSON = await (await fetch('/networks/' + selectedName + '/')).json(); //TODO : requête networks
    let downloadLink = window.document.createElement('a');
    downloadLink.href = window.URL.createObjectURL(new Blob([JSON.stringify(networkJSON, null, 2)], {type: "application/json"}));
    downloadLink.download = selectedName + '.json';

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
};

networkDlButton.onmouseenter = () => {
    networkText.innerHTML = "Download selected network file"
};

networkDlButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

endlessCheckBox.onclick = () => {
    duration.disabled = endlessCheckBox.checked;
};

saveConfigButton.onclick = async () => {
    let configJson = {
        'travelers_per_day': document.getElementById('conf-travelers-0').value,
        'trip_limit': document.getElementById('conf-travelers-1').value,
        'traveler_limit': document.getElementById('conf-travelers-2').value,
        'ascent_descent_duration': document.getElementById('conf-travelers-3').value,
        'morning_peak_hour': document.getElementById('conf-travelers-4').value,
        'evening_peak_hour': document.getElementById('conf-travelers-5').value,

        'activity_and_residential_percent': document.getElementById('conf-probabilities-0').value,
        'city_percent': document.getElementById('conf-probabilities-1').value,
        'activity_and_residential_fluctuation': document.getElementById('conf-probabilities-2').value,

        'max_speed': document.getElementById('conf-capsule-0').value,
        'number_of_capsules': document.getElementById('conf-capsule-1').value,
        'station_refill': document.getElementById('conf-capsule-2').checked,
        'fulfill_period': document.getElementById('conf-capsule-3').value,

        'switched_cost': document.getElementById('conf-routing-0').value,
        'my_timer': document.getElementById('conf-routing-1').value,
        'timer_other': document.getElementById('conf-routing-2').value,

        'real_time': document.getElementById('conf-simulation-0').checked,
        'endless': document.getElementById('conf-simulation-1').checked,
        'duration': document.getElementById('conf-simulation-2').value,
        'start_hour': document.getElementById('conf-simulation-3').value,
        'logs': document.getElementById('conf-simulation-4').checked,
    };

    for (const input of document.getElementsByClassName('form-control')) {
        let inputClassList = input.nextElementSibling.classList;
        if (input.checkValidity()) {
            inputClassList.add('text-muted');
            inputClassList.remove('form-text-error');
        } else if (inputClassList.contains('form-text')) {
            inputClassList.remove('text-muted');
            inputClassList.add('form-text-error');
        }
    }

    if (!document.getElementById('config-form').checkValidity()) {
        return;
    }

    saveConfigButton.disabled = true;
    resetConfigButton.disabled = true;


    await fetch('/config/save/', { //TODO: requête save
        method: "POST",
        body: JSON.stringify(configJson)
    });
    saveConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    updateConfigPanel();
    saveConfigButton.title = "Config has been saved !";
    setTimeout(() => {
        saveConfigButton.removeAttribute("title");
    }, 2000);
};

resetConfigButton.onclick = async () => {
    saveConfigButton.disabled = true;
    resetConfigButton.disabled = true;
    await fetch('/config/reset/', { //TODO : requête reset
        method: "POST"
    });
    saveConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    updateConfigPanel();
    resetConfigButton.title = "Config has been reset !";
    setTimeout(() => {
        resetConfigButton.removeAttribute("title");
    }, 2000);
};
