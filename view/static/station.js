import {Entity} from "./entity.js";
const {RegularPolygon} = Konva;

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
        super(hintsLayer);
        super.add(outerShape);
        super.add(innerShape);
        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
        this.unselect();
    }
    set _x(value) {
        super._x = value;
        this.__outerShape.x(value);
        this.__innerShape.x(value);
    }
    get _x() {
        return super._x;
    }
    set _y(value) {
        super._y = value;
        this.__outerShape.y(value);
        this.__innerShape.y(value);
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
    set _travelerCount(value) {
        this.__travelerCount = value;
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
    set _travelerBoardingSpeeds(value) {
        this.__travelerBoardingSpeeds = value;
    }
    get _travelerBoardingSpeeds() {
        return this.__travelerBoardingSpeeds;
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
    update(json) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const podCount = json["pods"]["count"];
        const podMax = json["pods"]["max"];
        const podPos = json["pods"]["pos"];
        const podBoarding = json["pods"]["boarding"];
        const travelerCount = json["travelers"]["count"];
        const travelerAllTimeCount = json["travelers"]["all_time_count"];
        const travelerAverageWaitingTime = json["travelers"]["average_waiting_time"];
        const travelerBoardingSpeeds = json["travelers"]["boarding_speeds"];
        const stationType = json["station_type"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._podCount = podCount;
        this._podMax = podMax;
        this._podPos = podPos;
        this._podBoarding = podBoarding;
        this._travelerCount = travelerCount;
        this._travelerAllTimeCount = travelerAllTimeCount;
        this._travelerAverageWaitingTime = travelerAverageWaitingTime;
        this._travelerBoardingSpeeds = travelerBoardingSpeeds;
        this._stationType = stationType;
    }
}
