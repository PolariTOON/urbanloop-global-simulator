import {state} from "./state.js";

const {Chart} = Highcharts;

const statsTab = document.getElementById("stats-content");
const statsObject = document.createElement("div");
const statsText = document.createElement("div");
statsTab.append(statsObject, statsText);
const downloadStatsButton = document.getElementById("download-stats-button");

const chart = new Chart({
    chart: {
        renderTo: statsObject,
        type: "line",
        animation: false,
    },
    title: {
        text: "Detailed statistics",
    },
    xAxis: {
        ctitle: "Time",
        type: "datetime",
        tickPixelInterval: 150,
        maxZoom: 20000,
    },
    yAxis: {
        title: "Value",
        minPadding: .2,
        maxPadding: .2,
    },
    series: [
        {
            name: "Traveling pods",
            data: [],
            animation: {
                duration: 0,
            },
        },
        {
            name: "Travelers",
            data: [],
            animation: {
                duration: 0,
            },
        },
        {
            name: "Average waiting duration (in s)",
            data: [],
            animation: {
                duration: 0,
            },
        },
    ],
    credits: {
        enabled: false,
    },
    drilldown: {
        animation: {
            duration: 0,
        },
    },
});

state.addEventListener("load", (event) => {
    downloadStatsButton.download = "stats.txt";
    downloadStatsButton.href = "data:text/plain,";
});

state.addEventListener("unload", (event) => {
    downloadStatsButton.download = "";
    downloadStatsButton.removeAttribute("href");
    const series = chart.series;
    for (let i = 0; i < 3; ++i) {
        series[i].data = [];
    }
});

downloadStatsButton.addEventListener("click", async (event) => {
    if (!downloadStatsButton.hasAttribute("href")) {
        return;
    }
    const stats = `\
--- ${chart.title.element.textContent} ---

${chart.series.map((series) => {
        return `\
${series.name}:
    min: ${series.dataMin || 0}
    max: ${series.dataMax || 0}
    mean: ${series.data.reduce((previous, current) => {
            return previous + current;
    }, 0)}
`;
}).join(`\

`)}`;
    const blob = new Blob([stats], {
        type: "text/plain",
    });
    const url = URL.createObjectURL(blob);
    downloadStatsButton.href = url;
});

state.addEventListener("update", (event) => {
    const networkJSON = event.detail;
    const datetime = networkJSON["time"];
    const statsJSON = networkJSON["stats"];
    const podCount = statsJSON["nb_pod"];
    const travelerCount = statsJSON["nb_traveler"];
    const travelerAverageWaitingTime = statsJSON["waiting_time"];
    const key = datetime * 1000;
    const values = [podCount, travelerCount, travelerAverageWaitingTime];
    const series = chart.series;
    for (let i = 0; i < 3; ++i) {
        series[i].addPoint([key, values[i]], true, false);
    }
    const stats = `\
<dl>
    <dt>Traveling pods</dt>
    <dd>${podCount}</dd>
    <dt>Travelers</dt>
    <dd>${travelerCount}</dd>
    <dt>Average waiting duration (in s)</dt>
    <dd>${travelerAverageWaitingTime}</dd>
</dl>
`
    statsText.innerHTML = stats;
});
