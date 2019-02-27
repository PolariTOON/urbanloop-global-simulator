allTextForScaling = [];

class TextObject {
    constructor(x, y, text, size) {
        this.item = new PIXI.Text();
        this.size = Math.ceil(size - text.length / 4);
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
        this.name = new TextObject(this.data.x, networkDiv.offsetHeight - this.data.y, this.data.name, fontSize);
        this.outerCircle = new PIXI.Graphics();
        this.innerCircle = new PIXI.Graphics();
        this.borderWidth = borderWidth;
        this.loopWidth = loopWidth;

        this.initStyle();
        this.initBehavior();
    }

    initStyle() {
        let x = this.data.x;
        let y = networkDiv.offsetHeight - this.data.y;
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
    constructor(stationSetData, stationVarData, stationWidth = 15, borderWidth = 2) {
        this.setData = stationSetData;
        this.varData = stationVarData;
        this.circle = new PIXI.Graphics();
        this.stationWidth = stationWidth;
        this.borderWidth = borderWidth;

        this.initStyle();
        this.initBehavior();
    }

    initStyle() {
        let loop = getLoopById(this.setData.loop);
        let radiusAngle = -this.setData.angle * ((2 * Math.PI) / 360);
        let x = loop.x + Math.cos(radiusAngle) * loop.radius;
        let y = networkDiv.offsetHeight - loop.y + Math.sin(radiusAngle) * loop.radius;

        let color = 0xFFFFFF;
        let borderColor = 0x4672D3;
        let selectedColor = 0x86CA0F;

        this.circle.beginFill(borderColor);
        this.circle.drawCircle(x, y, this.stationWidth + this.borderWidth);
        this.circle.endFill();
        this.circle.beginFill(color);
        this.circle.drawCircle(x, y, this.stationWidth);
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
    constructor(switchSetData, switchVarData, switchWidth = 15, borderWidth = 2, connectWidth = 2) {
        this.setData = switchSetData;
        this.varData = switchVarData;
        this.inCircle = new PIXI.Graphics();
        this.outCircle = new PIXI.Graphics();
        this.connectLine = new PIXI.Graphics();
        this.switchWidth = switchWidth;
        this.borderWidth = borderWidth;
        this.connectWidth = connectWidth;

        this.initStyle();
        this.initBehavior();
    }

    initStyle() {
        let loopIn = getLoopById(this.setData.loopIn);
        let loopOut = getLoopById(this.setData.loopOut);
        let radiusAngleLoopIn = -this.setData.angleLoopIn * ((2 * Math.PI) / 360);
        let radiusAngleLoopOut = -this.setData.angleLoopOut * ((2 * Math.PI) / 360);
        let xIn = loopIn.x + Math.cos(radiusAngleLoopIn) * loopIn.radius;
        let yIn = networkDiv.offsetHeight - loopIn.y + Math.sin(radiusAngleLoopIn) * loopIn.radius;
        let xOut = loopOut.x + Math.cos(radiusAngleLoopOut) * loopOut.radius;
        let yOut = networkDiv.offsetHeight - loopOut.y + Math.sin(radiusAngleLoopOut) * loopOut.radius;

        let color = 0xFFFFFF;
        let borderColor = 0x6B0003;
        let connectColor = 0x000000;
        let selectedColor = 0x86CA0F;

        this.connectLine.lineStyle(this.connectWidth, connectColor);
        this.connectLine.moveTo(xIn, yIn);
        this.connectLine.lineTo(xOut, yOut);

        this.inCircle.beginFill(borderColor);
        this.inCircle.drawCircle(xIn, yIn, this.switchWidth + this.borderWidth);
        this.inCircle.endFill();
        this.inCircle.beginFill(color);
        this.inCircle.drawCircle(xIn, yIn, this.switchWidth);
        this.inCircle.endFill();

        this.outCircle.beginFill(borderColor);
        this.outCircle.drawCircle(xOut, yOut, this.switchWidth + this.borderWidth);
        this.outCircle.endFill();
        this.outCircle.beginFill(color);
        this.outCircle.drawCircle(xOut, yOut, this.switchWidth);
        this.outCircle.endFill();
    }

    initBehavior() {
        this.inCircle.interactive = true;
        this.outCircle.interactive = true;

        this.inCircle.on('pointerdown', () => {
            alert("Click on switch in");
        });

        this.outCircle.on('pointerdown', () => {
            alert("Click on switch out ");
        });
    }

    drawInto(stage) {
        stage.addChild(this.connectLine);
        stage.addChild(this.inCircle);
        stage.addChild(this.outCircle);
    }

    remove() {
        stage.addChild(this.connectLine);
        stage.removeChild(this.inCircle);
        stage.removeChild(this.outCircle);
    }
}

class CapsuleObject {
    constructor(capsuleData) {
    }
}