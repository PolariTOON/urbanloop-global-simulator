


export class Statisctics{
	//_nbTraveler
	constructor() {
        this._nbTraveler = 0;
        this._chart = null;
    }

	get nbTraveler(){
		return this._nbTraveler;
	}
	set nbTraveler(value) {
        this._nbTraveler = value;
    }
    get chart(){
		return this._chart;
	}
	set chart(value) {
        this._chart = value;
    }

	update(json){
		const nbTraveler = json["nb_traveler"];
		this._nbTraveler = nbTraveler;
		this._waiting_times = json["waiting_time"];
		this.updateChart();
		//console.log(this._waiting_times);

	}

	updateChart() {
	    var point = [Date.now(),this._nbTraveler];
	    var series = this._chart.series[0];
	    var shift = series.data.length > 200;
	    this._chart.series[0].addPoint(point, true, false);
	}

}