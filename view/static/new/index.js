import {state} from "./state.js";
import {init} from "./menu.js";
(async () => {
    const integer = /^(?:0|[1-9]\d*)$/;
    const url = new URL(location);
    let networkIndex = url.searchParams.get("id");
    let network = null;
    if (networkIndex !== null && networkIndex.match(integer)) {
        network = await (await fetch(`/networks/${networkIndex}/`, {
            method: "GET"
        })).json();
    } else {
        do {
            networkIndex = String(Math.random()).slice(2);
            network = await (await fetch(`/networks/${networkIndex}/`, {
                method: "GET"
            })).json();
        } while (network !== null);
        url.searchParams.set("id", networkIndex);
        history.replaceState(null, "", url);
    }
    state.networkIndex = networkIndex;
    init(network);
}) ();
