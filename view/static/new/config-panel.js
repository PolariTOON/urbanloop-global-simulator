let saveConfigButton = document.getElementById('config-save-button');
let resetConfigButton = document.getElementById('config-reset-button');
let fulfillPeriod = document.getElementById('conf-capsule-3');
let duration = document.getElementById('conf-simulation-2');
let endlessCheckBox = document.getElementById('conf-simulation-1');
let refillCheckBox = document.getElementById('conf-capsule-2');

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
}

refillCheckBox.onclick = () => {
    fulfillPeriod.disabled = !refillCheckBox.checked;
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
