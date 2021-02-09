import {Entity} from "./entity.js";
const {RegularPolygon} = Konva;
const {Text} = Konva;

const shadowColor = "#333"
const outerColor = "#f03";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";

export class Station extends Entity {
    // __outerShape;
    // __innerShape;
    // __podCount;
    // __podMax;
    // __travelerCount;
    // __travelerAllTimeCount;
    // __travelerAverageWaitingTime;
    // __stationType;
    constructor(hintsLayer) {
        const outerShape = new RegularPolygon({
            lineJoin: "round",
            lineCap: "round",
            sides: 3,
            radius: 20,
            strokeWidth: 1,
            stroke: shadowColor,
        });
        const innerShape = new RegularPolygon({
            listening: false,
            lineJoin: "round",
            lineCap: "round",
            sides: 3,
            radius: 10,
            strokeWidth: 1,
            fill: innerColor,
            stroke: shadowColor,
        });
        const textForTravelerCount = new Text({
            text: 'Simple Text',
            fontSize: 20,
            fontFamily: 'Calibri',
            fill: outerColor,
        });

/*
        outerShape.perfectDrawEnabled(false);
        innerShape.perfectDrawEnabled(false);
        outerShape.listening(false);
        innerShape.listening(false);
*/

        super(hintsLayer);
        super.add(outerShape);
        super.add(innerShape);
        super.add(textForTravelerCount);

        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
        this.__textForTravelerCount = textForTravelerCount;
        this._showing_travelers_waiting = false;

        this.unselect();
    }

    set _x(value) {
        super._x = value;
        this.__outerShape.x(value);
        this.__innerShape.x(value);
        this.__textForTravelerCount.x(value - 5);
    }
    get _x() {
        return super._x;
    }
    set _y(value) {
        super._y = value;
        this.__outerShape.y(value);
        this.__innerShape.y(value);
        this.__textForTravelerCount.y(value + 25);
    }
    get _y() {
        return super._y;
    }
    set _podCount(value) {
        this.__podCount = value;
    }
    get _podCount() {
        return this.__podCount;
    }
    set _podMax(value) {
        this.__podMax = value;
    }
    get _podMax() {
        return this.__podMax;
    }
    set _podPos(value) {
        this.__podPos = value;
    }
    get _podPos() {
        return this.__podPos;
    }
    set _podBoarding(value) {
        this.__podBoarding = value;
    }
    get _podBoarding() {
        return this.__podBoarding;
    }
    set _podFull(value) {
        this.__podFull = value;
    }
    get _podFull() {
        return this.__podFull;
    }

    set _travelerCount(value) 
    {
        this.__travelerCount = value;
        if (this._showing_travelers_waiting)
        {
            this.__textForTravelerCount.setText(value + "");
        }
        else
        {
            this.__textForTravelerCount.setText("");
        }
    }

    get _travelerCount() {
        return this.__travelerCount;
    }
    set _travelerAllTimeCount(value) {
        this.__travelerAllTimeCount = value;
    }
    get _travelerAllTimeCount() {
        return this.__travelerAllTimeCount;
    }
    set _travelerAverageWaitingTime(value) {
        this.__travelerAverageWaitingTime = value;
    }
    get _travelerAverageWaitingTime() {
        return this.__travelerAverageWaitingTime;
    }
    set _travelerBoardingTimes(value) {
        this.__travelerBoardingTimes = value;
    }
    get _travelerBoardingTimes() {
        return this.__travelerBoardingTimes;
    }
    set _stationType(value) {
        this.__stationType = value;
    }
    get _stationType() {
        return this.__stationType;
    }
    select() {
        this.__outerShape.fill(selectedOuterColor);
    }
    unselect() {
        this.__outerShape.fill(outerColor);
    }
    update(json, showing_travelers_waiting) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const podCount = json["pods"]["count"];
        const podMax = json["pods"]["max"];
        const podPos = json["pods"]["pos"];
        const podBoarding = json["pods"]["boarding"];
        const podFull = json["pods"]["full"];
        const travelerCount = json["travelers"]["count"];
        const travelerAllTimeCount = json["travelers"]["all_time_count"];
        const travelerAverageWaitingTime = json["travelers"]["average_waiting_time"];
        const travelerBoardingTimes = json["travelers"]["boarding_times"];
        const stationType = json["station_type"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._podCount = podCount;
        this._podMax = podMax;
        this._podPos = podPos;
        this._podBoarding = podBoarding;
        this._podFull = podFull;
        this._travelerCount = travelerCount;
        this._travelerAllTimeCount = travelerAllTimeCount;
        this._travelerAverageWaitingTime = travelerAverageWaitingTime;
        this._travelerBoardingTimes = travelerBoardingTimes;
        this._stationType = stationType;
        this._showing_travelers_waiting = showing_travelers_waiting;
    }
}
