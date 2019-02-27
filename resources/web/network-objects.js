allTextForScaling = [];

class TextObject {
    constructor(x, y, text, size) {
        this.item = new PIXI.Text();
        this.size = size - text.length / 2;
        this.item.anchor.set(0.5);
        this.item.text = text;
        this.item.x = x;
        this.item.y = y;
        this.item.style = new PIXI.TextStyle({
            fontFamily: "Georgia, serif",
            fontSize: this.size,
            fontVariant: "small-caps",
            fontWeight: "lighter"
        });

        allTextForScaling.push(this);
    }
}

class LoopObject {
    constructor(loopData, loopWidth = 4, borderWidth = 1, fontSize = 20) {
        this.data = loopData;
        this.name = new TextObject(this.data.x, this.data.y, this.data.name, fontSize);
        this.outerCircle = new PIXI.Graphics();
        this.innerCircle = new PIXI.Graphics();
        this.borderWidth = borderWidth;
        this.loopWidth = loopWidth;

        this.initStyle();
        this.initBehavior();
    }

    initStyle() {
        let x = this.data.x;
        let y = this.data.y;
        let radius = this.data.radius;
        let outerColor = 0x9C9C9C;
        let innerColor = 0xFFFFFF;
        let borderColor = 0x000000;
        let selectedColor = 0x86CA0F;

        this.outerCircle.lineStyle(this.borderWidth, borderColor);
        this.outerCircle.arc(x, y, radius + (this.loopWidth / 2), 0, 2 * Math.PI);
        this.outerCircle.beginFill(outerColor);
        this.outerCircle.drawCircle(x, y, radius + (this.loopWidth / 2));
        this.outerCircle.endFill();

        this.innerCircle.lineStyle(this.borderWidth, borderColor);
        this.innerCircle.arc(x, y, radius - (this.loopWidth / 2), 0, 2 * Math.PI);
        this.innerCircle.beginFill(innerColor);
        this.innerCircle.drawCircle(x, y, radius - (this.loopWidth / 2));
        this.innerCircle.endFill();
    }

    initBehavior() {
        this.outerCircle.interactive = true;
        this.innerCircle.interactive = true;

        let inOuterCircle = false;
        let outInnerCircle = false;
        this.outerCircle.on('pointerover', function () {
            inOuterCircle = true;
        });
        this.outerCircle.on('pointerout', function () {
            inOuterCircle = false;
        });
        this.innerCircle.on('pointerover', function () {
            outInnerCircle = false;
        });
        this.innerCircle.on('pointerout', function () {
            outInnerCircle = true;
        });

        this.outerCircle.on('pointerdown', () => {
            if (inOuterCircle && outInnerCircle) {
                alert("Click on Loop " + this.data.name);
            }
        });
    }

    drawInto(stage) {
        stage.addChild(this.outerCircle);
        stage.addChild(this.innerCircle);
        stage.addChild(this.name.item);
    }

    remove() {
        stage.removeChild(this.outerCircle);
        stage.removeChild(this.innerCircle);
        stage.removeChild(this.name.item);
    }
}


class StationObject {
    constructor(stationSetData, stationVarData, borderWidth = 2) {
        this.setData = stationSetData;
        this.varData = stationVarData;
        this.circle = new PIXI.Graphics();
        this.borderWidth = borderWidth;

        this.initStyle();
        this.initBehavior();
    }

    initStyle() {
        let loop = getLoopById(this.setData.loop);
        let conv = (2 * Math.PI) / 360;
        let x = loop.x - Math.cos(conv * (this.setData.angle + 90)) * loop.radius;
        let y = loop.y - Math.sin(conv * (this.setData.angle + 90)) * loop.radius;

        let color = 0xFFFFFF;
        let borderColor = 0x4672D3;
        let selectedColor = 0x86CA0F;

        this.circle.lineStyle(this.borderWidth, borderColor);
        this.circle.arc(x, y, 20 + this.borderWidth / 2, 0, 2 * Math.PI);
        this.circle.beginFill(color);
        this.circle.drawCircle(x, y, 20);
        this.circle.endFill();
    }

    initBehavior() {
        this.circle.interactive = true;

        this.circle.on('pointerdown', () => {
            alert("Click on station " + this.setData.name);
        });
    }

    drawInto(stage) {
        stage.addChild(this.circle);
    }

    remove() {
        stage.removeChild(this.circle);
    }
}


class SwitchObject {
    constructor(switchSetData, switchVarData) {
    }
}

class CapsuleObject {
    constructor(capsuleData) {
    }
}