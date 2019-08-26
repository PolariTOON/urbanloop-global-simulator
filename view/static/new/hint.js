const {Label, Tag, Text} = Konva;

const tagColor = "#333";
const textColor = "#fff";

export class Hint extends Label {
    // __tag;
    // __text;
    constructor() {
        const tag = new Tag({
            lineJoin: "round",
            lineCap: "round",
            pointerDirection: "down",
            pointerWidth: 20,
            pointerHeight: 10,
            cornerRadius: 4,
            fill: tagColor,
        });
        const text = new Text({
            lineJoin: "round",
            lineCap: "round",
            padding: 8,
            lineHeight: 1.25,
            fontFamily: "Helvetica, Arial, sans-serif",
            fontSize: 16,
            fill: textColor,
        });
        super({
            listening: false,
            visible: false,
            offsetY: 12,
        });
        super.add(tag);
        super.add(text);
        this.__tag = tag;
        this.__text = text;
    }
    set _name(value) {
        this.__text.text(value);
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
