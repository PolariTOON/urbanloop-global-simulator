import {updateConfigPanel} from "./tabs.js";
import {applyNetworkScene} from "./renderer.js";

(async () => {
    await applyNetworkScene();
    updateConfigPanel();
}) ();
