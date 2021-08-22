idList = {
  "vehicles": {
      "car": "car",
      "bicycle": "bicycle",
      "motorcycle": "motorcycle",
      "truck": "truck",
      "bus": "bus",
      "pedestrian": "pedestrian",
      "transport_other": "other"
  },
  "severity": {
      "fatality": 1,
      "hospitalisation": 2,
      "medicalTreatment": 3,
      "minorInjury": 4,
      "propertyDamage": 5
  },
  "nature": {
    "angle": 1,
    "collision": 2,
    "fall": 3,
    "headon": 4,
    "animal": 5,
    "object": 6,
    "parked": 7,
    "hitPed": 8,
    "noncollision": 9,
    "nature_other": 10,
    "overturned": 11,
    "rearend": 12,
    "sideswipe": 13,
    "extLoad": 14,
    "intLoad": 15
  },
  "crashType": {
    "ped": 1,
    "singleVeh": 2,
    "multiVeh": 3,
    "type_other": 4
  },
  "weather": {
    "clear": 1,
    "raining": 2,
    "fog": 3,
    "smoke": 4
  }
}

document.getElementById("dateMax").addEventListener("change", updateYearBounds);
document.getElementById("dateMin").addEventListener("change", updateYearBounds);
document.getElementById("applyFilters").addEventListener("pointerup", updateMap);
document.getElementById("showFilter").addEventListener("pointerup", showFilter);

initControls();
var map;
initMap();

function initControls() {
  // Initialise the collapsible list
  var elem = document.querySelector('.collapsible.expandable');
  var instance = M.Collapsible.init(elem, {
    accordion: false
  });

  // Initialise all dropdowns
  var selects = document.querySelectorAll('select');
  var instances = M.FormSelect.init(selects);

  var sidenavs = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(sidenavs);
}

function initMap() {
  disableApply();
  map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      })
    ],
    view: new ol.View({
      center: [16305945.73750275, -2206013.7191165173], // ol.proj.fromLonLat([144.25, -23.1]),
      zoom: 6.13,
      minZoom: 6,
      extent: [15523987.351939877, -3234740.7746837423, 17196894.49780245, -1255714.7470971544],
      constrainOnlyCenter: true
    })
  });
  enableApply();
}

function parseData(returnedData) {
  var vector = new ol.source.Vector();
  returnedData.forEach((item, i) => {
    var point = new ol.geom.Point(ol.proj.fromLonLat([item.location[0], item.location[1]]));
    var pointFeature = new ol.Feature({
      geometry: point,
      weight: item.severityindex/10
    });
    vector.addFeature(pointFeature);
  });
  var layers = new Array();
  map.getLayers().getArray()
      .filter(layer => layer.get('name') == 'heatmap' || layer.get('name') == 'bubble')
      .forEach(layer => layers.push(layer));
  var heatmapLayer = new ol.layer.Heatmap({
    source: vector,
    radius: 8
  });
  layers.forEach(layer => map.removeLayer(layer))
  heatmapLayer.set("name", "heatmap")
  map.addLayer(heatmapLayer);
}

function generateHeatMapPoints() {
  var data = new ol.source.Vector();
  for (var i = 0; i < 500; i++) {
    var point = new ol.geom.Point([Math.random() * 1672907.145862573 + 15523987.351939877, Math.random() * 1979026.0275865879 + -3234740.7746837423]);
    var pointFeature = new ol.Feature({
      geometry: point,
      weight: Math.random() * 15
    });
    data.addFeature(pointFeature);
  }
  var layers = new Array();
  map.getLayers().getArray()
      .filter(layer => layer.get('name') == 'heatmap' || layer.get('name') == 'bubble')
      .forEach(layer => layers.push(layer));
  var heatmapLayer = new ol.layer.Heatmap({
    source: data,
    radius: Math.random() * 15
  });
  layers.forEach(layer => map.removeLayer(layer))
  heatmapLayer.set("name", "heatmap")
  map.addLayer(heatmapLayer);
}

// Don't allow the year stop to be larger than year start
function updateYearBounds() {
  document.getElementById("dateMin").max = document.getElementById("dateMax").value;
  document.getElementById("dateMax").min = document.getElementById("dateMin").value;
}

function showFilter() {
  M.Sidenav.getInstance(document.getElementById("slide-out")).open();
}

function disableApply() {
  elementList = document.querySelectorAll("input").forEach((item) => {
    item.disabled = true;
  });

  document.getElementById("applyFilters").classList.add("disabled");
  document.getElementById("loader").style.display = "block";
}

function enableApply() {
  elementList = document.querySelectorAll("input").forEach((item) => {
    item.disabled = false;
  });
  document.getElementById("applyFilters").classList.remove("disabled");
  document.getElementById("loader").style.display = "none";
}

function generateWarning(type = "none") {
  enableApply();
  if(type == "none") {
    M.toast({html: "Error: Something happened", classes: "red rounded"});
  } else {
    enableApply();
    M.toast({html: "Error: No " + type + " type selected", classes: "red rounded"});
  }
}

function updateMap() {
  disableApply();

  requestBody = {};
  boundingBox = map.getView().calculateExtent(map.getSize());

  // These are commented out so that data from the entire state is fetched.
  // requestBody.corner1 = ol.proj.transform(boundingBox.slice(0,2), 'EPSG:3857', 'EPSG:4326');
  //requestBody.corner2 = ol.proj.transform(boundingBox.slice(2,4), 'EPSG:3857', 'EPSG:4326');
  requestBody.yearmax = parseInt(document.getElementById("dateMax").value);
  requestBody.yearmin = parseInt(document.getElementById("dateMin").value);
  requestBody.vehicle_types = [];
  requestBody.severity = [];
  requestBody.weather = [];
  requestBody.nature = [];
  requestBody.type = [];

  // Handle sealed/unsealed roads
  if(!document.getElementById("sealed").checked && !document.getElementById("unsealed").checked) {
    generateWarning("road");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(7);
    return;
  }
  if(document.getElementById("sealed").checked != document.getElementById("unsealed").checked) {
    requestBody.sealed = document.getElementById("sealed").checked;
  }

  // Handle lighting conditions
  if(!document.getElementById("daylight").checked && !document.getElementById("darkness1").checked
        && !document.getElementById("darkness2").checked
        && !document.getElementById("dawndusk").checked) {
    generateWarning("lighting conditions");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(5);
    return;
  }
  if(!(document.getElementById("daylight").checked && document.getElementById("darkness1").checked
        && document.getElementById("darkness2").checked && document.getElementById("dawndusk").checked)) {
    if(document.getElementById("darkness1").checked != document.getElementById("darkness2").checked) {
      requestBody.lit = document.getElementById("darkness1").checked;
    }

    if(document.getElementById("daylight").checked
        && !(document.getElementById("darkness1").checked || document.getElementById("darkness2"))) {
      requestBody.day = document.getElementById("daylight").checked;
    }

    requestBody.partialDaylight = document.getElementById("dawndusk").checked;
  }


  // Handle list of vehicles
  for (const [key, value] of Object.entries(idList.vehicles)) {
    if (document.getElementById(key).checked) {
      requestBody.vehicle_types.push(value);
    }
  }
  if (requestBody.vehicle_types.length == 0) {
    generateWarning("vehicle");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(0);
    return;
  }

  // Handle list of severity
  for (const [key, value] of Object.entries(idList.severity)) {
    if (document.getElementById(key).checked) {
      requestBody.severity.push(value);
    }
  }
  if (requestBody.severity.length == 0) {
    generateWarning("severity");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(2);
    return;
  }

  // Handle list of crash natures
  for (const [key, value] of Object.entries(idList.nature)) {
    if (document.getElementById(key).checked) {
      requestBody.nature.push(value);
    }
  }
  if (requestBody.nature.lenght == 0) {
    generateWarning("crash nature");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(3);
    return;
  }

  // Handle list of types
  for (const [key, value] of Object.entries(idList.crashType)) {
    if (document.getElementById(key).checked) {
      requestBody.type.push(value);
    }
  }
  if (requestBody.type.length == 0) {
    generateWarning("crash type");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(4);
    return;
  }

  // Handle list of weather
  for (const [key, value] of Object.entries(idList.weather)) {
    if (document.getElementById(key).checked) {
      requestBody.weather.push(value);
    }
  }
  if (requestBody.weather.length == 0) {
    generateWarning("weather");
    M.Collapsible.getInstance(document.getElementById("sidebar")).open(6);
    return;
  }
  console.dir(requestBody);

  var xhttp = new XMLHttpRequest();
  // xhttp.addEventListener("readystatechange", parseData);
  xhttp.onreadystatechange = function () {
      if (xhttp.readyState === 4 && xhttp.status === 200) {
          parseData(JSON.parse(xhttp.responseText));
      }
  };
  xhttp.open("POST", "http://api.crashmap.xyz/list_crashes", true);
  xhttp.send(JSON.stringify(requestBody));

  // Finally start the request
  // Set timeout
  setTimeout(enableApply, 5000);
}
