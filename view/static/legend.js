const {Label, Text} = Konva;

const textColor = "#333";

export class Legend extends Label {
    // __text;
    constructor() {
        const text = new Text({
            fontFamily: "Georgia, Times, serif",
            fontVariant: "small-caps",
            fontSize: 20,
            fill: textColor,
        });
        super({
            listening: false,
        });
        super.add(text);
        this.__text = text;
    }
    set _name(value) {
        this.__text.text(value);
        this.__text.offsetX(this.__text.width() / 2);
        this.__text.offsetY(this.__text.height() / 2);
    }
    get _name() {
        return this.__text.text();
    }
    set _x(value) {
        super.x(value);
    }
    get _x() {
        return super.x();
    }
    set _y(value) {
        super.y(value);
    }
    get _y() {
        return super.y();
    }
}
