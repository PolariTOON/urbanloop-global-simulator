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
        this.section = section;
        networkLayer.add(section);
        state.nodes.push(section);
        for (const pod of json["pods"]) {
            const p = new Pod(pod, json, loopsJSON, infoLayer);
            networkLayer.add(p);
            state.pods.set(pod["id"], p);
        }
    }
    update(json, loopsJSON, networkLayer, infoLayer) {
        this.section.update(json["section"]);
        for (const pod of json["pods"]) {
            if (state.pods.has(pod["id"])) {
                const p = state.pods.get(pod["id"]);
                p.update(pod, json, loopsJSON);
                p.keepFlag = 1;
            } else {
                const p = new Pod(pod, json, loopsJSON, infoLayer);
                p.keepFlag = 2;
                networkLayer.add(p);
                state.pods.set(pod["id"], p);
            }
        }
    }
}
