// Some elements are defined in the above file objects.js
let dataTab = document.getElementById("data-tab");
let configTab = document.getElementById("config-tab");
let interactTab = document.getElementById("interact-tab");
let viewTab = document.getElementById("view-tab");
let saveConfigButton = document.getElementById('config-save-button');
let jQuerySaveConfigButton = $('#config-save-button');
let permanentConfigButton = document.getElementById('config-permanent-button');
let jQueryPermanentConfigButton = $('#config-permanent-button');
let resetConfigButton = document.getElementById('config-reset-button');
let jQueryResetConfigButton = $('#config-reset-button');
let networkAddButton = document.getElementById('network-add-btn');
let jQueryNetworkAddButton = $('#network-add-btn');
let networkDlButton = document.getElementById('network-dl-btn');
let networkFavButton = document.getElementById('network-fav-btn');
let jQueryNetworkFavButton = $('#network-fav-btn');
let networkRemoveButton = document.getElementById('network-remove-btn');
let jQueryNetworkRemoveButton = $('#network-remove-btn');
let networkText = document.getElementById('network-text');
let networkSelection = document.getElementById('conf-topology-0');
let networkFileInput = document.getElementById('conf-topology-1');
let networkErrorText = document.getElementById('network-error-text');
let endlessCheckBox = document.getElementById('conf-simulation-1');
let startHour = document.getElementById('conf-simulation-2');
let permanentConfigChange = false;

function updateDataPanel() {
    let data = "";
    // gather data
    if (selectedObject instanceof Loop) {
        data += "<p>Loop " + selectedObject.json["name"] + "</p>";
        data += "<p>Circumference : " + selectedObject.json["size"] + "</p>";
        data += "<p>Center coordinates : [" + selectedObject.json["x"] + ";" + selectedObject.json["y"] + "]</p>";
        data += "<p>Elements :";
        let elements = selectedObject.json["objects"];
        for (let key in elements) {
            data += "<br>&nbsp;" + key;
        }//TODO CHECK WORKS
        data += "</p>";
    } else if (selectedObject instanceof Switch) {
        data += "<p>Switch #" + selectedObject.json["id"] + "</p>";
        data += "<p>Loop of the switch: " + selectedObject.json["my_loop_name"] + "</p>";
        data += "<p><br>&nbsp; Next element:" + selectedObject.json["next_element_name"] + "</p>";
        data += "<p>Loop switched: " + selectedObject.json["other_loop_name"] + "</p>";
        data += "<p><br>&nbsp; Next element:" + selectedObject.json["next_other_element_name"] + "</p>";
        data += "<p>Size of the link: " + selectedObject.json["size"] + "</p>";
        //data += "<p>Routing table: " + selectedObject.json["table"] + "</p>";
    } else if (selectedObject instanceof Station) {
        data += "<p>Station " + selectedObject.json["name"] + "</p>";
        data += "<p>Type de station: " + selectedObject.json["type"] + "</p>";
        data += "<p>Loop: " + selectedObject.json["outerCircle"] + "</p>";
        data += "<p>Capacity: " + selectedObject.json["capacity"] + "</p>";
        data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
        data += "<p>Waiting travelers: " + selectedObject.json["nb_travelers"] + "</p>";
        data += "<p>Capsules:" + selectedObject.json["nb_capsules"];
        for (k in selectedObject.json["capsules"]) {
            data += "<br>&nbsp;Capsule #" + selectedObject.json["capsules"][k];
        }
        data += "</p>";
    } else if (selectedObject instanceof Warehouse) {
        data += "<p>Warehouse #" + selectedObject.json["id"] + "</p>";
        data += "<p>Loop: " + selectedObject.json["outerCircle"] + "</p>";
        data += "<p>Capacity: " + selectedObject.json["capacity"] + "</p>";
        data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
        data += "<p>Capsules:" + selectedObject.json["nb_capsules"];
        /*for (k in selectedObject.json["capsules"]) {
            data += "<br>&nbsp;<br>&nbsp;Capsule #" + selectedObject.json["capsules"][k];
        }*/
        data += "</p>";
    } else if (selectedObject instanceof Capsule) {
        data += "<p> Capsule #" + selectedObject.json["id"] + "</p>";
        data += "<p>Contains a traveler: " + (selectedObject.json["travelerNumber"] !== 0) + "</p>";
        if (selectedObject.json["destination"] !== undefined) {
            data += "<p>Destination: " + selectedObject.json["destination"] + "</p>";
        }
        data += "<p>Current Loop: " + selectedObject.json["outerCircle"] + "</p>";
        data += "<p>Last or current element: " + selectedObject.json["current_element"] + "</p>";
        data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
    } else {
        data += "<p>Nothing selected.</p>";
    }
    dataTab.innerHTML = data;
}

function updateConfigPanel() {
    $.getJSON('/config.json/0', function (configJSON) {
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

        document.getElementById('conf-routing-0').value = configJSON['switched_cost'];
        document.getElementById('conf-routing-1').value = configJSON['my_timer'];
        document.getElementById('conf-routing-2').value = configJSON['timer_other'];

        let realTimeCheckBox = document.getElementById('conf-simulation-0');
        let endlessCheckBox = document.getElementById('conf-simulation-1');
        realTimeCheckBox.checked = false;
        endlessCheckBox.checked = false;
        startHour.disabled = false;
        if (['true', 'True'].includes(configJSON['real_time'])) {
            realTimeCheckBox.checked = true;
        }
        if (['true', 'True'].includes(configJSON['endless'])) {
            endlessCheckBox.checked = true;
            startHour.disabled = true;
        }
        document.getElementById('conf-simulation-2').value = configJSON['duration'];
        document.getElementById('conf-simulation-3').value = configJSON['start_hour'];
    });

    updateNetworkSelection();
}

function updateNetworkSelection() {
    while (networkSelection.firstChild) {
        networkSelection.removeChild(networkSelection.firstChild);
    }
    $.getJSON('/network-files.json', function (listNetworkFileNameJSON) {
        listNetworkFileNameJSON.forEach(networkFileNameJSON => {
            let option = document.createElement('option');
            option.innerHTML = networkFileNameJSON['fileName'];
            networkSelection.appendChild(option)
        });
    });
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

function waitConfigChange() {
    let waitingConfigLoaded = true;
    let waitStart = new Date();

    while (waitingConfigLoaded && (new Date() - waitStart) < 1000) {
        $.getJSON('/config-loaded-signal.json', function (configLoadedSignalJSON) {
            waitingConfigLoaded = !configLoadedSignalJSON['configLoadedSignal'];
        });
    }

    saveConfigButton.disabled = false;
    permanentConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    updateConfigPanel();
}

function waitNetworkSignal(signalUrl) {
    let waitingNetworkSignal = true;
    let waitStart = new Date();

    while (waitingNetworkSignal && (new Date() - waitStart) < 1000) {
        $.getJSON(signalUrl, function (networkSignalJSON) {
            waitingNetworkSignal = !networkSignalJSON['networkSignal'];
        });
    }

    changeNetworkButtonState(false);
    updateNetworkSelection();
}

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
    reader.onload = (event) => {
        $.ajaxSetup({async: false});

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

        $.post('/add-network-file/' + name, {
            data: JSON.stringify(parsedJSON)
        });
        waitNetworkSignal('/network-added-signal.json');
        jQueryNetworkAddButton.tooltip({
            html: true,
            title: "<b style='color: greenyellow'>Network file has been added !</b>"
        });
        jQueryNetworkAddButton.tooltip('show');
        setTimeout(() => {
            jQueryNetworkAddButton.tooltip('hide');
            jQueryNetworkAddButton.tooltip('dispose');
        }, 3000);
        $.ajaxSetup({async: true});
    };

    reader.onerror = () => {
        networkErrorText.innerHTML = "An error occurred while loading file";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
    };
};

networkAddButton.onclick = () => {
    $('#conf-topology-1').trigger('click');
};

networkAddButton.onmouseenter = () => {
    networkText.innerHTML = "Add network json file"
};

networkAddButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

networkRemoveButton.onclick = () => {
    let selectedName = networkSelection[networkSelection.selectedIndex].value;

    if (selectedName.includes('default: ')) {
        networkErrorText.innerHTML = "Cannot remove default file";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
        return;
    }

    resetNetworkErrorText();
    changeNetworkButtonState(true);

    $.ajaxSetup({async: false});
    $.get('/remove-network-file/' + selectedName);
    waitNetworkSignal('/network-removed-signal.json');
    $('#conf-topology-0').trigger('change');
    jQueryNetworkRemoveButton.tooltip({
        html: true,
        title: "<b style='color: #ea0000'>Selected network has been removed !</b>"
    });
    jQueryNetworkRemoveButton.tooltip('show');
    setTimeout(() => {
        jQueryNetworkRemoveButton.tooltip('hide');
        jQueryNetworkRemoveButton.tooltip('dispose');
    }, 3000);
    $.ajaxSetup({async: true});
};

networkRemoveButton.onmouseenter = () => {
    networkText.innerHTML = "Remove selected network from the list"
};

networkRemoveButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

networkDlButton.onclick = () => {
    let selectedName = networkSelection[networkSelection.selectedIndex].value;
    let isDefault = false;
    if (selectedName.includes('default: ')) {
        isDefault = true;
        selectedName = selectedName.replace('default: ', '');
    }

    $.getJSON(String.prototype.concat('/dl-network-file.json/', selectedName, '/', isDefault ? '1' : '0'), function (networkJSON) {
        let downloadLink = window.document.createElement('a');
        downloadLink.href = window.URL.createObjectURL(new Blob([JSON.stringify(networkJSON, null, 2)], {type: "application/json"}));
        downloadLink.download = selectedName.replace('default : ', '') + '.json';

        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    });
};

networkDlButton.onmouseenter = () => {
    networkText.innerHTML = "Download selected network file"
};

networkDlButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

networkFavButton.onclick = () => {
    let selectedName = networkSelection[networkSelection.selectedIndex].value;

    if (selectedName.includes('default: ')) {
        networkErrorText.innerHTML = "Selected network file is already the default one";
        networkErrorText.classList.remove('text-muted');
        networkErrorText.classList.add('form-text-error');
        return;
    }

    resetNetworkErrorText();
    changeNetworkButtonState(true);

    $.ajaxSetup({async: false});
    $.get('/change-default-network-file/' + selectedName);
    waitNetworkSignal('/network-default-changed-signal.json');
    jQueryNetworkFavButton.tooltip({
        html: true,
        title: "<b style='color: #f6cc24'>Selected network is now the default one !</b>"
    });
    jQueryNetworkFavButton.tooltip('show');
    setTimeout(() => {
        jQueryNetworkFavButton.tooltip('hide');
        jQueryNetworkFavButton.tooltip('dispose');
    }, 3000);
    $.ajaxSetup({async: true});
};

networkFavButton.onmouseenter = () => {
    networkText.innerHTML = "Make selected network file the default one"
};

networkFavButton.onmouseleave = () => {
    networkText.innerHTML = String();
};

endlessCheckBox.onclick = () => {
    startHour.disabled = !!endlessCheckBox.checked;
};

saveConfigButton.onclick = () => {
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

        'switched_cost': document.getElementById('conf-routing-0').value,
        'my_timer': document.getElementById('conf-routing-1').value,
        'timer_other': document.getElementById('conf-routing-2').value,

        'real_time': document.getElementById('conf-simulation-0').checked,
        'endless': document.getElementById('conf-simulation-1').checked,
        'duration': document.getElementById('conf-simulation-2').value,
        'start_hour': document.getElementById('conf-simulation-3').value
    };

    Array.prototype.forEach.call(document.getElementsByClassName('form-control'), function (input) {
        let inputClassList = input.nextElementSibling.classList;
        if (input.checkValidity()) {
            inputClassList.add('text-muted');
            inputClassList.remove('form-text-error');
        } else if (inputClassList.contains('form-text')) {
            inputClassList.remove('text-muted');
            inputClassList.add('form-text-error');
        }
    });

    if (!document.getElementById('config-form').checkValidity()) {
        return;
    }

    saveConfigButton.disabled = true;
    permanentConfigButton.disabled = true;
    resetConfigButton.disabled = true;

    $.ajaxSetup({async: false});
    $.post(String.prototype.concat('/config.json/', permanentConfigChange ? '1' : '0'), {
        data: JSON.stringify(configJson)
    });
    waitConfigChange();
    jQuerySaveConfigButton.tooltip({
        html: true,
        title: "<b style='color: greenyellow'>Config has been saved !</b>"
    });
    jQuerySaveConfigButton.tooltip('show');
    setTimeout(() => {
        jQuerySaveConfigButton.tooltip('hide');
        jQuerySaveConfigButton.tooltip('dispose');
    }, 2000);
    $.ajaxSetup({async: true});
};

permanentConfigButton.onclick = () => {
    if (permanentConfigChange) {
        permanentConfigChange = false;
        permanentConfigButton.innerHTML = "<i class='far fa-square'></i> Temporary";
        permanentConfigButton.classList.remove("btn-danger");
        permanentConfigButton.classList.add("btn-info");
        jQueryPermanentConfigButton.tooltip('hide');
        jQueryPermanentConfigButton.tooltip('dispose');
    } else {
        permanentConfigChange = true;
        permanentConfigButton.innerHTML = "<i class='fas fa-check-square'></i> Permanent";
        permanentConfigButton.classList.remove("btn-info");
        permanentConfigButton.classList.add("btn-danger");
        jQueryPermanentConfigButton.tooltip({
            html: true,
            title: "<b style='color: #ea0000'>Save will overwrite default config with above data</b>"
        });
        jQueryPermanentConfigButton.tooltip('show');
    }
};

permanentConfigButton.onmouseleave = () => {
    if (permanentConfigChange) {
        jQueryPermanentConfigButton.tooltip('hide');
    }
};

resetConfigButton.onclick = () => {
    saveConfigButton.disabled = true;
    permanentConfigButton.disabled = true;
    resetConfigButton.disabled = true;
    $.ajaxSetup({async: false});
    $.get('/reset-config');
    waitConfigChange();
    jQueryResetConfigButton.tooltip({
        html: true,
        title: "<b style='color: deepskyblue'>Config has been reset !</b>"
    });
    jQueryResetConfigButton.tooltip('show');
    setTimeout(() => {
        jQueryResetConfigButton.tooltip('hide');
        jQueryResetConfigButton.tooltip('dispose');
    }, 2000);
    $.ajaxSetup({async: true});
};






