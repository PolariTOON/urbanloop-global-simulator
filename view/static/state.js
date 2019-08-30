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
        this._loops = [];
        this._bridges = [];
        this._nodes = [];
        this._pods = new Map();
        this._selectedEntity = null;
        this._viewBox = null;
        this._origin = null;
    }
    get networkIndex() {
        return this._networkIndex;
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
    _load(detail) {
        this._unload();
        if (this._loaded || detail === null) {
            return;
        }
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
        state.dispatchEvent(new CustomEvent("unload"));
        this._loaded = false;
    }
    _update(detail) {
        if (!this._loaded || !this._running) {
            return;
        }
        state.dispatchEvent(new CustomEvent("update", {detail}));
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
        state.dispatchEvent(new CustomEvent("pause"));
        this._running = false;
    }
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
}

export const state = new State();
