class LoopObject {
    constructor(loopData, loopWidth = 5) {
        this.data = loopData;
        this.outerCircle = new PIXI.Graphics();
        this.innerCircle = new PIXI.Graphics();
        this.loopWidth = loopWidth;
        this.color = 0x000000;
        this.selectedColor = 0x86CA0F;

        this.initStyle();
        this.initBehavior();
    }

    initStyle() {
        this.outerCircle.lineStyle(this.loopWidth, this.color);
        this.outerCircle.arc(this.data.x, this.data.y, this.data.radius, 0, 2 * Math.PI);
        this.outerCircle.hitArea = new PIXI.Circle(this.data.x, this.data.y, this.data.radius + (this.loopWidth / 2));

        this.innerCircle.hitArea = new PIXI.Circle(this.data.x, this.data.y, this.data.radius - (this.loopWidth / 2));
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

        this.outerCircle.on('pointerdown', function () {
            if (inOuterCircle && outInnerCircle) {
                alert("Click on Loop");
            }
        });
    }

    drawInto(stage) {
        stage.addChild(this.outerCircle);
        stage.addChild(this.innerCircle);
    }
}


class StationObject {
    constructor(stationSetData, stationVarData) {
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