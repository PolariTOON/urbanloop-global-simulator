const switchColor = 'rgb(200, 40, 40)';
const switchSelectedColor = 'rgb(255, 200, 20)';

export class Switch {
    constructor(switchJSON, switchRadius = 12, switchWidth = 4) {
        this.json = switchJSON;
        this.uuid = switchJSON['uuid'];
        this.id = switchJSON['id'];

        const xIn = switchJSON['xIn'];
        const yIn = getNetworkDivSize().height - switchJSON['yIn'];
        const xOut = switchJSON['xOut'];
        const yOut = getNetworkDivSize().height - switchJSON['yOut'];
        const semiWidth = Math.floor(switchWidth / 2);

        this.innerInCircle = new Konva.Circle({
            x: xIn,
            y: yIn,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerInCircle = new Konva.Circle({
            name: this.uuid,
            x: xIn,
            y: yIn,
            radius: switchRadius + semiWidth,
            fill: switchColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.innerOutCircle = new Konva.Circle({
            x: xOut,
            y: yOut,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerOutCircle = new Konva.Circle({
            name: this.uuid,
            x: xOut,
            y: yOut,
            radius: switchRadius + semiWidth,
            fill: switchColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.link = new Konva.Line({
            points: [xIn, yIn, xOut, yOut],
            stroke: 'black',
            strokeWidth: 2,
        });

        this.arrow = new Konva.Arrow({
            points: [xIn, yIn, (xIn + xOut) / 2, (yIn + yOut) / 2],
            pointerLength: 10,
            pointerWidth: 10,
            fill: 'black',
            stroke: 'black',
            strokeWidth: 2
        });

        this.infoIn = new Konva.Label({
            x: xIn,
            y: yIn,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.infoOut = new Konva.Label({
            x: xOut,
            y: yOut,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.infoIn.add(new Konva.Tag({
            fill: 'black',
            pointerDirection: 'down',
            pointerWidth: 10,
            pointerHeight: 10,
            lineJoin: 'round',
            shadowColor: 'black',
            shadowBlur: 10,
            shadowOffset: 10,
            shadowOpacity: 0.2
        }));

        this.infoOut.add(new Konva.Tag({
            fill: 'black',
            pointerDirection: 'down',
            pointerWidth: 10,
            pointerHeight: 10,
            lineJoin: 'round',
            shadowColor: 'black',
            shadowBlur: 10,
            shadowOffset: 10,
            shadowOpacity: 0.2
        }));

        this.infoIn.add(
            new Konva.Text({
                text: switchJSON['nameIn'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.infoOut.add(
            new Konva.Text({
                text: switchJSON['nameOut'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.innerInCircle, this.outerInCircle, this.infoIn);
        initBehaviors(this, this.innerOutCircle, this.outerOutCircle, this.infoOut);

        networkLayer.add(this.arrow);
        networkLayer.add(this.link);
        networkLayer.add(this.outerInCircle);
        networkLayer.add(this.innerInCircle);
        networkLayer.add(this.outerOutCircle);
        networkLayer.add(this.innerOutCircle);
        infoLayer.add(this.infoIn);
        infoLayer.add(this.infoOut);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.arrow.stroke(switchSelectedColor);
        this.arrow.fill(switchSelectedColor);
        this.outerInCircle.fill(switchSelectedColor);
        this.outerOutCircle.fill(switchSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.arrow.stroke('black');
        this.arrow.fill('black');
        this.outerInCircle.fill(switchColor);
        this.outerOutCircle.fill(switchColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const height = getNetworkDivSize().height;
        const xIn = this.json['xIn'];
        const yIn = height - this.json['yIn'];
        const xOut = this.json['xOut'];
        const yOut = height - this.json['yOut'];

        this.innerInCircle.y(yIn);
        this.outerInCircle.y(yIn);
        this.innerOutCircle.y(yOut);
        this.outerOutCircle.y(yOut);
        this.infoIn.y(yIn);
        this.infoOut.y(yOut);
        this.link.points([xIn, yIn, xOut, yOut]);
        this.arrow.points([xIn, yIn, (xIn + xOut) / 2, (yIn + yOut) / 2]);
    }

    updateScale(value) {
        this.innerInCircle.scaleX(value);
        this.innerInCircle.scaleY(value);
        this.outerInCircle.scaleX(value);
        this.outerInCircle.scaleY(value);
        this.innerOutCircle.scaleX(value);
        this.innerOutCircle.scaleY(value);
        this.outerOutCircle.scaleX(value);
        this.outerOutCircle.scaleY(value);
        this.infoIn.scaleX(value);
        this.infoIn.scaleY(value);
        this.infoOut.scaleX(value);
        this.infoOut.scaleY(value);
        this.link.strokeWidth(2 * value);
        this.arrow.strokeWidth(2 * value);
        this.arrow.pointerWidth(10 * value);
        this.arrow.pointerLength(10 * value);
    }
}

function updateSwitchFromJSON(switchJSON) {

}