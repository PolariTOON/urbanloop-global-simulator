const closedColor = "red"
const selectedPathColor = "#0fc";


async function getJSON(url) {
    const fetchInit = {
        method: "GET",
    };
    return (await fetch(url, fetchInit)).json();
}

async function postJSON(url, content) {
    const fetchInit = {
        method: "POST",
    };
    if (typeof content !== "undefined") {
        fetchInit.headers = {
            "Content-Type": "application/json;charset=utf-8"
        };
        fetchInit.body = JSON.stringify(content);
    }
    return (await fetch(url, fetchInit)).json();
}

class State extends EventTarget { // TODO: utiliser un polyfill pour Safari
    constructor() {
        super();
        this._networkIndex = "";
        this._loaded = false;
        this._running = false;
        this._rate = 0;
        this._maxRate = 0;
        this._jerky = 0;
        this._loops = [];
        this._bridges = [];
        this._nodes = [];
        this._pods = new Map();
        this._selectedEntity = null;
        this._viewBox = null;
        this._origin = null;
        this._stats = null;
        this._chart = null;
        //this._showingTravelersWaiting = false;
    }
    get chart(){
        return this._chart;
    }
    set chart(value){
        this._chart = value;
    }
    get stats(){
        return this._stats;
    }
    set stats(value){
        this._stats = value;
    }
    get networkIndex() {
        return this._networkIndex;
    }
    get rate() {
        return this._rate;
    }
    get maxRate() {
        return this._maxRate;
    }
    get jerky() {
        return this._jerky;
    }
    get loops() {
        return this._loops;
    }
    get bridges() {
        return this._bridges;
    }
    get nodes() {
        return this._nodes;
    }
    get pods() {
        return this._pods;
    }
    set selectedEntity(value) {
        this._selectedEntity = value;
    }
    get selectedEntity() {
        return this._selectedEntity;
    }
    set viewBox(value) {
        this._viewBox = value;
    }
    get viewBox() {
        return this._viewBox;
    }
    set origin(value) {
        this._origin = value;
    }
    get origin() {
        return this._origin;
    }
    /*
    get showingTravelersWaiting() {
        return this._showingTravelersWaiting;
    }
    */
    _load(detail) {
        this._unload();
        if (this._loaded || detail === null) {
            return;
        }
        this._rate = detail["rate"];
        this._maxRate = detail["max_rate"];
        this._jerky = detail["jerky"];
        this.dispatchEvent(new CustomEvent("load", {detail}));
        this._loaded = true;
        if (detail.running) {
            this._play();
        }
    }
    _unload() {
        if (!this._loaded) {
            return;
        }
        this._pause();
        this._rate = 0;
        this._maxRate = 0;
        this._jerky = false;
        this.dispatchEvent(new CustomEvent("unload"));
        this._loaded = false;
    }
    _update(detail) {
        if (!this._loaded || !this._running) {
            return;
        }
        this._rate = detail["rate"];
        this._maxRate = detail["max_rate"];
        this._jerky = detail["jerky"];
        this.dispatchEvent(new CustomEvent("update", {detail}));
    }
    _play() {
        if (!this._loaded || this._running) {
            return;
        }
        this.dispatchEvent(new CustomEvent("play"));
        this._running = true;
    }
    _pause() {
        if (!this._loaded || !this._running) {
            return;
        }
        this.dispatchEvent(new CustomEvent("pause"));
        this._running = false;
    }
    _close() {
        if (!this._loaded || !this._running) {
            return;
        }
        this.dispatchEvent(new CustomEvent("close"));
    }
    _decelerate() {
        if (!this._loaded) {
            return;
        }
        this._rate = Math.max(this._rate - 1, 0);
        this.dispatchEvent(new CustomEvent("decelerate"));
    }
    _accelerate() {
        if (!this._loaded) {
            return;
        }
        this._rate = Math.min(this._rate + 1, this._maxRate);
        this.dispatchEvent(new CustomEvent("accelerate"));
    }
    _resize() {
        this.dispatchEvent(new CustomEvent("resize"));
    }
    _downloadStats(){
        //alert('Hello world!');
        //var fileSystem=new ActiveXObject("Scripting.FileSystemObject");
        let blob = new Blob([this._stats.getStats()], { type: 'text/plain' });
        let url = window.URL.createObjectURL(blob);
        const fileName = "test.txt";
        let link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
            document.body.removeChild(link);
        }, 100);

        //this.dispatchEvent(new CustomEvent("downloadStats"));
    }


    // Show travelers number for each station
    /*
    _showTravelersWaiting()
    {
        alert('showTravelersWaiting');
        this_showingTravelersWaiting = !this_showingTravelersWaiting;
    }
    */
    // Show travelers number for each station
    

    async reload() {
        const integer = /^(?:0|[1-9]\d*)$/;
        const url = new URL(location);
        let networkIndex = url.searchParams.get("id");
        let network = null;
        if (networkIndex !== null && networkIndex.match(integer) && Number(networkIndex) <= Number.MAX_SAFE_INTEGER) {
            network = await getJSON(`/networks/${networkIndex}/`);
        } else {
            do {
                networkIndex = String(Math.random() * (Number.MAX_SAFE_INTEGER + 1));
                network = await getJSON(`/networks/${networkIndex}/`);
            } while (network !== null);
            url.searchParams.set("id", networkIndex);
            history.replaceState(null, "", url);
        }
        this._networkIndex = networkIndex;
        if (network === null) {
            return;
        }
        this._load(network);
    }
    async load(input) {
        const output = await postJSON(`/networks/${this._networkIndex}/`, input);
        if (output === null) {
            return;
        }
        this._load(output);
    }
    async unload() {
        const output = await postJSON(`/networks/${this._networkIndex}/`, null);
        if (output !== null) {
            return;
        }
        this._unload();
    }
    async update() {
        const output = await getJSON(`/networks/${this._networkIndex}/`);
        if (output === null) {
            return;
        }
        this._update(output);
    }
    async play() {
        const output = await postJSON(`/networks/${this._networkIndex}/clock/play/`);
        if (!output) {
            return;
        }
        this._play();
    }
    async close() {
        var section_id = this._selectedEntity["_id"]
        var section_name = this._selectedEntity["_name"]
        const output = await postJSON(`/networks/${this._networkIndex}/close/${section_name}/`);
        if (!output) {
            return;
        }
        if (this._selectedEntity.__closed == 0){
            this._selectedEntity.__innerPath.fill(closedColor);
            this._selectedEntity.__innerPath.stroke(closedColor);
            this._selectedEntity.__closed = 1;
        }
        else {
            this._selectedEntity.__innerPath.fill(selectedPathColor);
            this._selectedEntity.__innerPath.stroke(selectedPathColor);
            this._selectedEntity.__closed = 0;
        }
        this._close();
    }
    async pause() {
        const output = await postJSON(`/networks/${this._networkIndex}/clock/pause/`);
        if (!output) {
            return;
        }
        this._pause();
    }
    async decelerate() {
        const output = await postJSON(`/networks/${this._networkIndex}/clock/decelerate/`);
        if (!output) {
            return;
        }
        this._decelerate();
    }
    async accelerate() {
        const output = await postJSON(`/networks/${this._networkIndex}/clock/accelerate/`);
        if (!output) {
            return;
        }
        this._accelerate();
    }

    async show_travelers_waiting() 
    {
        const output = await postJSON(`/networks/${this._networkIndex}/travelersWaiting/show/`);
        if (!output) 
        {
            return;
        }
    }
    async hide_travelers_waiting() 
    {
        const output = await postJSON(`/networks/${this._networkIndex}/travelersWaiting/hide/`);
        if (!output) 
        {
            return;
        }
    }

    async resize() {
        this._resize();
    }

    async downloadStats(){
        this._downloadStats();
    }

}

export const state = new State();
