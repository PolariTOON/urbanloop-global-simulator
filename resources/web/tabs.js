// Some elements are defined in the above file objects.js
let dataTab = document.getElementById("data-tab");
let configTab = document.getElementById("config-tab");
let interactTab = document.getElementById("interact-tab");
let viewTab = document.getElementById("view-tab");
let saveConfigButton = document.getElementById('config-save-button');
let permanentConfigButton = document.getElementById('config-permanent-button');
let resetConfigButton = document.getElementById('config-reset-button');
let networkAddButton = document.getElementById('network-add-btn');
let networkDlButton = document.getElementById('network-dl-btn');
let networkFavButton = document.getElementById('network-fav-btn');
let networkRemoveButton = document.getElementById('network-remove-btn');
let networkText = document.getElementById('network-text');
let networkSelection = document.getElementById('conf-topology-0');
let networkFileInput = document.getElementById('conf-topology-1');
let networkErrorText = document.getElementById('network-error-text');
let refillCheckBox = document.getElementById('conf-capsule-2');
let fulfillPeriod = document.getElementById('conf-capsule-3');
let endlessCheckBox = document.getElementById('conf-simulation-1');
let duration = document.getElementById('conf-simulation-2');
let permanentConfigChange = false;

function updateDataPanel() {
    let data = "";
    // gather data
    if (selectedObject instanceof Loop) {
        data += "<p>Loop: " + selectedObject.json["name"] + "</p>";
        data += "<p>Circumference: " + selectedObject.json["size"] + "</p>";
        data += "<p>Center coordinates: [" + selectedObject.json["x"] + ";" + selectedObject.json["y"] + "]</p>";
        data += "<p>Clockwise: " + selectedObject.json["clockwise"] + "</p>";
        data += "<p>Elements: ";
        let elements = selectedObject.json["objects"];
        for (key in elements) {
            data += "<br>&nbsp;" + elements[key];
        }
        data += "</p>";
    } else if (selectedObject instanceof Switch) {
        data += "<p>Switch n°" + selectedObject.json["id"] + "</p>";
        data += "<p>Loop of the switch: " + selectedObject.json["my_loop_name"] + "</p>";
        data += "<p>&nbsp; Next element : " + selectedObject.json["next_element_name"] + "</p>";
        data += "<p>Loop switched: " + selectedObject.json["other_loop_name"] + "</p>";
        data += "<p>&nbsp; Next element: " + selectedObject.json["next_other_element_name"] + "</p>";
        data += "<p>Size of the link: " + selectedObject.json["size"] + "</p>";
        //data += "<p>Routing table: " + selectedObject.json["table"] + "</p>";
    } else if (selectedObject instanceof Station) {
        data += "<p>Station: " + selectedObject.json["name"] + "</p>";
        data += "<p>Station Type: " + selectedObject.json["type"] + "</p>";
        data += "<p>Loop: " + selectedObject.json["outerCircle"] + "</p>";
        data += "<p>Capacity: " + selectedObject.json["capacity"] + "</p>";
        data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
        data += "<p>Waiting travelers: " + selectedObject.json["nb_travelers"] + "</p>";
        data += "<p>Capsules: " + selectedObject.json["nb_capsules"];
        for (k in selectedObject.json["capsules"]) {
            data += "<br>&nbsp;Capsule #" + selectedObject.json["capsules"][k];
        }
        data += "</p>";
    } else if (selectedObject instanceof Warehouse) {
        data += "<p>Warehouse n°" + selectedObject.json["id"] + "</p>";
        data += "<p>Loop: " + selectedObject.json["outerCircle"] + "</p>";
        data += "<p>Capacity: " + selectedObject.json["capacity"] + "</p>";
        data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
        data += "<p>Capsules: " + selectedObject.json["nb_capsules"];
        /*for (k in selectedObject.json["capsules"]) {
            data += "<br>&nbsp;<br>&nbsp;Capsule #" + selectedObject.json["capsules"][k];
        }*/
        data += "</p>";
    } else if (selectedObject instanceof Capsule) {
        data += "<p>Capsule n°" + selectedObject.json["id"] + "</p>";
        data += "<p>Contains a traveler: " + (selectedObject.json["travelerNumber"] !== 0) + "</p>";
        let destination = selectedObject.json["destination"] === undefined ? "None" : selectedObject.json["destination"];
        data += "<p>Destination: " + destination + "</p>";
        data += "<p>Current Loop: " + selectedObject.json["outerCircle"] + "</p>";
        data += "<p>Last or current element: " + selectedObject.json["current_element"] + "</p>";
        data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
    } else {
        data += "<p>Nothing selected.</p>";
    }
    dataTab.innerHTML = data;
}

async function updateConfigPanel() {
    const configJSON = await (await fetch('/config.json/0')).json();
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
    const listNetworkFileNameJSON = await (await fetch('/network-files.json')).json();
    for (const networkFileNameJSON of listNetworkFileNameJSON) {
        let option = document.createElement('option');
        option.innerHTML = networkFileNameJSON['fileName'];
        networkSelection.appendChild(option);
    }
}

function changeNetworkButtonState(disabled = false) {
    networkAddButton.disabled = disabled;
    networkDlButton.disabled = disabled;
    networkFavButton.disabled = disabled;
    networkRemoveButton.disabled = disabled;
}

function resetNetworkErrorText() {
    networkErrorText.innerHTML = "Select, add, remove or download a network JSON file";
    networkErrorText.classList.remove('form-text-error');
    networkErrorText.classList.add('text-muted');
}

async function waitConfigChange() {
    let waitingConfigLoaded = true;
    let waitStart = new Date();

    while (waitingConfigLoaded && (new Date() - waitStart) < 1000) {
        const configLoadedSignalJSON = await (await fetch('/config-loaded-signal.json')).json();
        waitingConfigLoaded = !configLoadedSignalJSON['configLoadedSignal'];
    }

    saveConfigButton.disabled = false;
    permanentConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    updateConfigPanel();
}

async function waitNetworkSignal(signalUrl) {
    let waitingNetworkSignal = true;
    let waitStart = new Date();

    while (waitingNetworkSignal && (new Date() - waitStart) < 1000) {
        const networkSignalJSON = await (await fetch(signalUrl)).json();
        waitingNetworkSignal = !networkSignalJSON['networkSignal'];
    }

    changeNetworkButtonState(false);
    updateNetworkSelection();
}

refillCheckBox.onclick = () => {
    fulfillPeriod.disabled = !refillCheckBox.checked;
};

networkSelection.onchange = () => {
    networkErrorText.innerHTML = "Select, add, remove or download a network JSON file";
    networkErrorText.classList.remove('form-text-error');
    networkErrorText.classList.add('text-muted');

    let selectedName = networkSelection[networkSelection.selectedIndex].value;
    let isDefault = false;
    if (selectedName.includes('default: ')) {
        isDefault = true;
        selectedName = selectedName.replace('default: ', '');
    }

    applyNetworkScene(selectedName, isDefault)
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

        await fetch('/add-network-file/' + name, {
            method: 'POST',
            body: JSON.stringify(parsedJSON)
        });
        await waitNetworkSignal('/network-added-signal.json');
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

    if (selectedName.includes('default: ')) {
        networkErrorText.innerHTML = "Cannot remove default file";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
        return;
    }

    resetNetworkErrorText();
    changeNetworkButtonState(true);

    await fetch('/remove-network-file/' + selectedName);
    await waitNetworkSignal('/network-removed-signal.json');
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
    let isDefault = false;
    if (selectedName.includes('default: ')) {
        isDefault = true;
        selectedName = selectedName.replace('default: ', '');
    }

    const networkJSON = await (await fetch('/dl-network-file.json/', selectedName + '/' + (isDefault ? '1' : '0'))).json();
    let downloadLink = window.document.createElement('a');
    downloadLink.href = window.URL.createObjectURL(new Blob([JSON.stringify(networkJSON, null, 2)], {type: "application/json"}));
    downloadLink.download = selectedName.replace('default : ', '') + '.json';

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

networkFavButton.onclick = async () => {
    let selectedName = networkSelection[networkSelection.selectedIndex].value;

    if (selectedName.includes('default: ')) {
        networkErrorText.innerHTML = "Selected network file is already the default one";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
        return;
    }

    resetNetworkErrorText();
    changeNetworkButtonState(true);

    await fetch('/change-default-network-file/' + selectedName);
    await waitNetworkSignal('/network-default-changed-signal.json');
    networkFavButton.title = "Selected network is now the default one !";
    setTimeout(() => {
        networkFavButton.removeAttribute("title");
    }, 3000);
};

networkFavButton.onmouseenter = () => {
    networkText.innerHTML = "Make selected network file the default one"
};

networkFavButton.onmouseleave = () => {
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
    permanentConfigButton.disabled = true;
    resetConfigButton.disabled = true;


    await fetch('/config.json/' + (permanentConfigChange ? '1' : '0'), {
        method: "POST",
        body: JSON.stringify(configJson)
    });
    await waitConfigChange();
    saveConfigButton.title = "Config has been saved !";
    setTimeout(() => {
        saveConfigButton.removeAttribute("title");
    }, 2000);
};

permanentConfigButton.onclick = () => {
    if (permanentConfigChange) {
        permanentConfigChange = false;
        permanentConfigButton.innerHTML = "<i class='far fa-square'></i> Temporary";
        permanentConfigButton.classList.remove("btn-danger");
        permanentConfigButton.classList.add("btn-info");
        permanentConfigButton.removeAttribute("title");
    } else {
        permanentConfigChange = true;
        permanentConfigButton.innerHTML = "<i class='fas fa-check-square'></i> Permanent";
        permanentConfigButton.classList.remove("btn-info");
        permanentConfigButton.classList.add("btn-danger");
        permanentConfigButton.title = "Save will overwrite default config with above data";
    }
};

permanentConfigButton.onmouseleave = () => {
    if (permanentConfigChange) {
        permanentConfigButton.removeAttribute("title");
    }
};

resetConfigButton.onclick = async () => {
    saveConfigButton.disabled = true;
    permanentConfigButton.disabled = true;
    resetConfigButton.disabled = true;
    await fetch('/reset-config');
    await waitConfigChange();
    resetConfigButton.title = "Config has been reset !"
    setTimeout(() => {
        resetConfigButton.removeAttribute("title");
    }, 2000);
};
