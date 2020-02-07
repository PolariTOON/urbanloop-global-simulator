


export class Statisctics{
	//_nbTraveler

	constructor(chartOptions) {
        this._nbTraveler = 0;
        this._chart = null;
        this.chartOptions = chartOptions;
        this._datetime = 0;
        this._waiting_time = 0;
        this._nbPod = 0;

    }

	get nbTraveler(){
		return this._nbTraveler;
	}
	set nbTraveler(value) {
        this._nbTraveler = value;
    }
    get waitingTime(){
		return this._waiting_time;
	}
	set waitingTime(value) {
        this._waiting_time = value;
    }
    get nbPod(){
		return this._nbPod;
	}
	set nbPod(value) {
        this.nbPod = value;
    }
    get chart(){
		return this._chart;
	}
	set chart(value) {
        this._chart = value;
    }
     get datetime(){
		return this._datetime;
	}
	set datetime(value) {
        this._datetime = value;
    }

	update(json){
		const nbTraveler = json["nb_traveler"];
		this._nbTraveler = nbTraveler;
		this._waiting_time = json["waiting_time"];
		this._nbPod = json["nb_pod"];
		this.updateChart();
		//console.log(this._waiting_times);

	}

	updateChart() {
	    var point = [this._datetime*1000,this._nbTraveler];
	    var series = this._chart.series[0];
	    var shift = series.data.length > 200;
	    this._chart.series[0].addPoint(point, true, false);

	    var point1 = [this._datetime*1000,this._waiting_time];
	    var series1 = this._chart.series[1];
	    var shift1 = series1.data.length > 200;
	    this._chart.series[1].addPoint(point1, true, false);

	    var point2 = [this._datetime*1000,this._nbPod];
	    var series2 = this._chart.series[2];
	    var shift2 = series2.data.length > 200;
		this._chart.series[2].addPoint(point2, true, false);
	}

	restartChart(){
		this._chart.destroy();
		this._chart = new Highcharts.Chart(this.chartOptions);
    	this._chart.series[0].setData([]);
    	this._chart.series[1].setData([]);
    	this._chart.series[2].setData([]);
	}

	getStats(){
		var res = "--- Detailed statisctis ---\n\n";
		res += "Number of traveler:\n";
		res += "\tmin: "+ this._chart.series[0].dataMin;
		res += "\tmax: "+ this._chart.series[0].dataMax;

		//let sum = this._chart.series[0].data.reduce((previous, current) => current += previous);
		//let avg = sum / this._chart.series[0].data.length;
		//res += "\tmean: "+ avg;
		//console.log(this._chart.series[0].data);

		res += "\nNumber of pods:\n";
		res += "\tmin: "+ this._chart.series[2].dataMin;
		res += "\tmax: "+ this._chart.series[2].dataMax;

		res += "\nWaiting time\n";
		res += "\tmin: "+ this._chart.series[1].dataMin;
		res += "\tmax: "+ this._chart.series[1].dataMax;
		//res += typeof(this._chart.series[0]);
		//res += "\mmean: "+ Math.sum(this._chart.series[0])/this._chart.series[0].length;
		 //res+= "Total duration: " + this._datetime-2880000;
		return res;
	}
}