import {applyNetworkScene} from "./network.js";

export function fetchTimeout(timeout, url, options) {
    const controller = new AbortController();
    const {signal} = controller;
    setTimeout(() => controller.abort(), timeout);
    return fetch(url, {...options, signal});
}

(async () => {
    await applyNetworkScene();
    updateConfigPanel();
}) ();