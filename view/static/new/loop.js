import {appState, getNetworkDivSize, initBehaviors} from "./network.js";
import {defaultPodWidth} from "./pod.js";

const loopColor = 'rgb(156, 156, 156)';
const loopSelectedColor = 'rgb(255, 200, 20)';

export class Loop {
    constructor(loopJSON) {
        this.json = loopJSON;
        this.id = loopJSON['id'];
        const x = loopJSON['x'];
        const y = getNetworkDivSize().height - loopJSON['y'];

        this.text = new Konva.Text({
            name: this.uuid,
            x: x,
            y: y,
            text: loopJSON['name'],
            fontFamily: "Georgia, serif",
            fontSize: 20,
            fontVariant: "small-caps",
            fill: 'black'
        });
        this.text.offsetX(this.text.width() / 2);
        this.text.offsetY(this.text.height() / 2);

        initBehaviors(this, this.innerCircle, this.outerCircle);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        networkLayer.add(this.text);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.outerCircle.fill(loopSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.outerCircle.fill(loopColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.json['y'];
        this.innerCircle.y(y);
        this.outerCircle.y(y);
        this.text.y(y);
    }

    updateScale(value) {
        const semiWidth = ((defaultPodWidth + 3) * appState.objectScale) / 2;
        const strokeWidth = semiWidth / 2.5;
        this.innerCircle.radius(this.json['radius'] - semiWidth);
        this.outerCircle.radius(this.json['radius'] + semiWidth);
        this.innerCircle.strokeWidth(strokeWidth);
        this.outerCircle.strokeWidth(strokeWidth);
        this.text.scaleX(value);
        this.text.scaleY(value);
    }
}

