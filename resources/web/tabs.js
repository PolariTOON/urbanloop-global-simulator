let dataTab = document.getElementById("data-tab");
let configTab = document.getElementById("config-tab");
let interractTab = document.getElementById("interract-tab");
let viewTab = document.getElementById("view-tab");

let selectedTab = dataTab;

generateSelectedTab();

function generateSelectedTab() {
  switch (selectedTab) {
    case dataTab:
      generateDataPanel();
      break;
    case configTab:
      generateConfigPanel();
      break;
    case interractTab:
      generateDataPanel();
      break;
    case viewTab:
      generateViewPanel()
      break;
  }
}

function generateDataPanel() {
  // update navbar
  selectedTab.classList.remove("active");
  dataTab.classList.add("active");
  selectedTab = dataTab;
  
  let div = document.createElement("div");
  div.id = "tab-content";
  let data = "";
  // gather data
  if (selectedObject instanceof Loop) {
    data += "<p>Loop " + selectedObject.json["name"] + "</p>";
    data += "<p>Circumference : " + selectedObject.json["size"] + "</p>";
    data += "<p>Center coordinates : [" + selectedObject.json["x"] + ";" + selectedObject.json["y"] + "]</p>";
    data += "<p>Elements :"
    let elements = selectedObject.json["objects"];
    for (key in elements) {
      element = elements[key];
      console.log(element);
      if (element["name"] !== undefined) {
        data += "<br>&nbsp;Station " + element["name"];
      } else {
        if (element["nameIn"].includes("=>")) {
          data += "<br>&nbsp;Switch out " + element["id"] + " to " + element["other_loop_name"];
        } else {
          data += "<br>&nbsp;Switch in " + element["id"] + " from " + element["my_loop_name"]
        }
      }
    }
    data += "</p>";
  } else if (selectedObject instanceof Switch) {
    data += "<p>Switch #" + selectedObject.json["id"] + "</p>";
    data += "<p>Loop of the switch: " + selectedObject.json["my_loop_name"] + "</p>";
    data += "<p>Next element:";
    data += "<br>&nbsp;" + selectedObject.json["next_element_name"] + "</p>";
    data += "<p>Loop switched: " + selectedObject.json["other_loop_name"] + "</p>";
    data += "<p>Next element:";
    data += "<br>&nbsp;" + selectedObject.json["next_other_element_name"] + "</p>";
    data += "<p>Size of the link: " + selectedObject.json["size"] + "</p>";
    data += "<p>Routing table: " + selectedObject.json["table"] + "</p>";
  } else if (selectedObject instanceof Station) {
    data += "<p>Station " + selectedObject.json["name"] + "</p>";
    data += "<p>Loop: " + selectedObject.json["loop"] + "</p>";
    /* WARNING station_type attribute is weird
    data += "<p>Station type: ";
    switch (selectedObject.json["type"]) {
      case 0:
        data += "neutral</p>";
        break;
      case 1:
        data += "activity zone</p>";
        break;
      case 2:
        data += "residential zone</p>";
        break;
      case 3:
        data += "down town</p>";
        break;
    }*/
    data += "<p>Capacity: " + selectedObject.json["capacity"] + "</p>";
    data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
    data += "<p>Capsules:";
    for (k in selectedObject.json["capsules"]) {
      data += "<br>&nbsp;Capsule #" + selectedObject.json["capsules"][k];
    }
    data += "</p>";
  } else if (selectedObject instanceof Capsule) {
    data += "Capsule #" + selectedObject.json["id"];
    data += "<p>Contains a traveler: " + selectedObject.json["travelerNumber"] !== 0 + "</p>";
    if (selectedObject.json["destination"] !== undefined) {
        data += "<p>Destination: " + selectedObject.json["destination"] + "</p>";
    }
    data += "<p>Current Loop: " + selectedObject.json["loop"] + "</p>";
    data += "<p>Last or current element: " + selectedObject.json["current_element"] + "</p>";
    data += "<p>Next element: " + selectedObject.json["next_element"] + "</p>";
  } else {
    data += "Nothing selected.";
  }
  div.innerHTML = data;
  document.getElementById("panel-div").replaceChild(div, document.getElementById("tab-content"));
}

function generateConfigPanel() {
  // update navbar
  selectedTab.classList.remove("active");
  configTab.classList.add("active");
  selectedTab = configTab;
  // show current config
  let configForm = document.createElement("form");
  configForm.id = "tab-content";
  // TODO
  /*
  // load config

  // TRAVELERS category
  let content = `
  <p>TRAVELERS</p>
  <div class="form-group row">
    <label for="travalersPerDay" class="offset-sm-1 col-sm-5 col-form-label">Email</label>
    <input type="text" class="col-sm-5 form-control" id="travalersPerDay" value="alo"/>
  </div>
  `;
  configForm.innerHTML = content;
  document.getElementById("panel-div").replaceChild(configForm, document.getElementById("tab-content"));
  */
}

function generateInterractPanel() {
  // update navbar
  selectedTab.classList.remove("active");
  interractTab.classList.add("active");
  selectedTab = interractTab;
  // TODO
}

function generateViewPanel() {
  // update navbar
  selectedTab.classList.remove("active");
  viewTab.classList.add("active");
  selectedTab = viewTab;
  // TODO
}