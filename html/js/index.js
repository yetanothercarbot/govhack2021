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
  }
}

document.getElementById("dateMax").addEventListener("change", updateYearBounds);
document.getElementById("dateMin").addEventListener("change", updateYearBounds);
document.getElementById("applyFilters").addEventListener("pointerup", updateMap);

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
  var elems = document.querySelectorAll('select');
  var instances = M.FormSelect.init(elems);
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

function generatePoints() {
  var data = new ol.source.Vector();
  for (var i = 0; i < 40; i++) {
    var point = new ol.geom.Point([Math.random() * 1672907.145862573 + 15523987.351939877, Math.random() * 1979026.0275865879 + -3234740.7746837423]);
    var pointFeature = new ol.Feature({
      geometry: point,
      weight: Math.random() * 15
    });
    data.addFeature(pointFeature);
  }
  var heatmapLayer = new ol.layer.Heatmap({
    source: data,
    radius: Math.random() * 20
  });
  map.addLayer(heatmapLayer);
}

// Don't allow the year stop to be larger than year start
function updateYearBounds() {
  document.getElementById("dateMin").max = document.getElementById("dateMax").value;
  document.getElementById("dateMax").min = document.getElementById("dateMin").value;
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

function updateMap() {
  setTimeout(disableApply, 200);

  requestBody = {};
  boundingBox = map.getView().calculateExtent(map.getSize());

  requestBody.corner1 = ol.proj.transform(boundingBox.slice(0,2), 'EPSG:3857', 'EPSG:4326');
  requestBody.corner2 = ol.proj.transform(boundingBox.slice(2,4), 'EPSG:3857', 'EPSG:4326');
  requestBody.yearmax = document.getElementById("dateMax").value;
  requestBody.yearmin = document.getElementById("dateMin").value;
  requestBody.vehicle_types = [];
  requestBody.severity = [];


  for (const [key, value] of Object.entries(idList.vehicles)) {
    if (document.getElementById(key).checked) {
      requestBody.vehicle_types.push(value);
    }
  }

  for (const [key, value] of Object.entries(idList.severity)) {
    if (document.getElementById(key).checked) {
      requestBody.
    }
  }
  console.dir(requestBody);

  // Set timeout
  setTimeout(enableApply, 5000);
}
