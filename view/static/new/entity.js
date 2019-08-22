import {Hint} from "./hint.js";
const {Group} = Konva;
export class Entity extends Group {
    // __hint;
    // __name;
    // __x;
    // __y;
    constructor(infoLayer) {
        const hint = new Hint();
        super();
        infoLayer.add(hint);
        this.__hint = hint;
    }
    set _name(value) {
        super.name(value);
        this.__name = value;
        this.__hint._name = value;
    }
    get _name() {
        return this.__name;
    }
    set _x(value) {
        super.x(value);
        super.offsetX(value);
        this.__x = value;
        this.__hint._x = value;
    }
    get _x() {
        return this.__x;
    }
    set _y(value) {
        super.y(value);
        super.offsetY(value);
        this.__y = value;
        this.__hint._y = value;
    }
    get _y() {
        return this.__y;
    }
    select() {}
    unselect() {}
    update() {}
    scale(...args) {
        const that = super.scale(...args);
        if (that !== this) {
            return that;
        }
        const {x, y} = super.scale();
        this.__hint.scale({
            x,
            y,
        });
        return that;
    }
    destroy() {
        const that = super.destroy();
        this.__hint.destroy();
        return that;
    }
    showHint(...args) {
        return this.__hint.show(...args);
    }
    hideHint(...args) {
        return this.__hint.hide(...args);
    }
}
