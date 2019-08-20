import {state} from "./state.js";
const {Group, Label, Tag, Text} = Konva;
export class Entity extends Group {
    constructor(options, infoLayer) {
        super(options);
        const {label, x, y} = options;
        this._hint = new Label({
            x,
            y,
            opacity: 0.75,
            visible: false,
            listening: false
        });
        this._hint.add(new Tag({
            fill: "black",
            pointerDirection: "down",
            pointerWidth: 10,
            pointerHeight: 10,
            lineJoin: "round",
            shadowColor: "black",
            shadowBlur: 10,
            shadowOffset: 10,
            shadowOpacity: 0.2
        }));
        this._hint.add(new Text({
            text: label,
            fontFamily: "sans-serif",
            fontSize: 18,
            padding: 5,
            fill: "white"
        }));
        infoLayer.add(this._hint);
        state.labels.push(this._hint);
    }
    showHint() {
        return this._hint.show();
    }
    hideHint() {
        return this._hint.hide();
    }
    scaleHint(...args) {
        return this._hint.scale(...args);
    }
    destroyHint(...args) {
        return this._hint.destroy(...args);
    }
    select() {}
    unselect() {}
    update(options) {
        const {x, y} = options;
        const xy = {x, y};
        this._hint.position(xy);
    }
}
