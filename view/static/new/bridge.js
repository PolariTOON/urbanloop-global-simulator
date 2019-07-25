import {state} from "./state.js";
import {Pod} from "./pod.js";
import {Section} from "./section.js";

export class Bridge {
    constructor(json, switchIn, switchOut, loopsJSON, networkLayer, infoLayer) {
        const name = json["name"];
        const x = (switchOut.x() + switchIn.x()) / 2;
        const y = (switchOut.y() + switchIn.y()) / 2;
        this.name = name;
        this.x = x;
        this.y = y;
        const section = new Section(json["section"], switchOut, switchIn, false, infoLayer);
        networkLayer.add(section);
        state.objects.push(section);
        for (const pod of json["pods"]) {
            const p = new Pod(pod, json, false, loopsJSON, infoLayer);
            networkLayer.add(p);
            state.objects.push(p);
        }
    }
}
