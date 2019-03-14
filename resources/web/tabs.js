let dataTab = document.getElementById("data-tab");
let configTab = document.getElementById("config-tab");
let interactTab = document.getElementById("interact-tab");
let viewTab = document.getElementById("view-tab");
let saveConfigButton = document.getElementById('config-save-button');
let permanentConfigButton = document.getElementById('config-permanent-button');
let resetConfigButton = document.getElementById('config-reset-button');
let endlessCheckBox = document.getElementById('conf-simulation-1');
let startHour = document.getElementById('conf-simulation-2');
let permanent = false;

function updateDataPanel() {
    let data = "";
    // gather data
    if (selectedObject instanceof Loop) {
        data += "<p>Loop " + selectedObject.json["name"] + "</p>";
        data += "<p>Circumference : " + selectedObject.json["size"] + "</p>";
        data += "<p>Center coordinates : [" + selectedObject.json["x"] + ";" + selectedObject.json["y"] + "]</p>";
        data += "<p>Elements :"
        let elements = selectedObject.json["objects"];
        for (key in elements) {
            data += "<br>&nbsp;" + elements[key];
        }
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
    $.get('/config.json/0', function (configJSON) {
        document.getElementById('conf-travelers-0').value = configJSON['travelers_per_day'];
        document.getElementById('conf-travelers-1').value = configJSON['trip_limit'];
        document.getElementById('conf-travelers-2').value = configJSON['traveler_limit'];
        document.getElementById('conf-travelers-3').value = configJSON['ascent_descent_duration'];
        document.getElementById('conf-travelers-4').value = configJSON['morning_peak_hour'];
        document.getElementById('conf-travelers-5').value = configJSON['evening_peak_hour'];

        //document.getElementById('conf-topology-0').value = configJSON['network_file'];

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
}

function blockTimeoutConfigButtons(timeout = 1000) {
    saveConfigButton.disabled = true;
    permanentConfigButton.disabled = true;
    resetConfigButton.disabled = true;
    setTimeout(() => {
        saveConfigButton.disabled = false;
        permanentConfigButton.disabled = false;
        resetConfigButton.disabled = false;
        updateConfigPanel();
    }, timeout);
}

saveConfigButton.onclick = () => {
    let configJson = {
        'travelers_per_day': document.getElementById('conf-travelers-0').value,
        'trip_limit': document.getElementById('conf-travelers-1').value,
        'traveler_limit': document.getElementById('conf-travelers-2').value,
        'ascent_descent_duration': document.getElementById('conf-travelers-3').value,
        'morning_peak_hour': document.getElementById('conf-travelers-4').value,
        'evening_peak_hour': document.getElementById('conf-travelers-5').value,

        //'network_file': document.getElementById('conf-topology-0').value,

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

    $.ajaxSetup({async: false});
    $.post(String.prototype.concat('/config.json/', permanent ? '1' : '0'), {
        data: JSON.stringify(configJson)
    });
    blockTimeoutConfigButtons();
    $.ajaxSetup({async: true});
};

permanentConfigButton.onclick = () => {
    updateConfigPanel();
    if (permanent) {
        permanent = false;
        permanentConfigButton.innerHTML = "<i class='far fa-square'></i> Temporary"
        permanentConfigButton.classList.remove("btn-danger");
        permanentConfigButton.classList.add("btn-info");
        $('#config-permanent-button').tooltip('hide');
        $('#config-permanent-button').tooltip('dispose');
    } else {
        permanent = true;
        permanentConfigButton.innerHTML = "<i class='fas fa-check-square'></i> Permanent"
        permanentConfigButton.classList.remove("btn-info");
        permanentConfigButton.classList.add("btn-danger");
        $('#config-permanent-button').tooltip({
            html: true,
            title: "<b>Save will overwrite default config with above data</b>"
        });
        $('#config-permanent-button').tooltip('show');
    }

};

permanentConfigButton.onmouseleave = () => {
    if (permanent) {
        $('#config-permanent-button').tooltip('hide');
    }
};

resetConfigButton.onclick = () => {
    $.ajaxSetup({async: false});
    $.get('/reset-config');
    blockTimeoutConfigButtons();
    $.ajaxSetup({async: true});
};

endlessCheckBox.onclick = () => {
    startHour.disabled = !!endlessCheckBox.checked;
};






