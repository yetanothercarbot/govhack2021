document.getElementById("dateMax").addEventListener("change", updateYearBounds);
document.getElementById("dateMin").addEventListener("change", updateYearBounds);
document.getElementById("applyFilters").addEventListener("pointerup", updateMap);

var map;
initMap();

// Don't allow the year stop to be larger than year start
function updateYearBounds() {
  document.getElementById("dateMin").max = document.getElementById("dateMax").value;
  document.getElementById("dateMax").min = document.getElementById("dateMin").value;
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
      zoom: 6.13
    })
  });
  enableApply();
}

function disableApply() {
  elementList = ["motorcycle", "bus", "truck", "dateMin", "dateMax"];
  elementList.forEach((item) => {
    document.getElementById(item).disabled = true;
  });

  document.getElementById("applyFilters").classList.add("disabled");
  document.getElementById("loader").style.display = "block";
}

function enableApply() {
  elementList = ["motorcycle", "bus", "truck", "dateMin", "dateMax"];
  elementList.forEach((item) => {
    document.getElementById(item).disabled = false;
  });
  document.getElementById("applyFilters").classList.remove("disabled");
  document.getElementById("loader").style.display = "none";
}

function updateMap() {
  console.warn("Disable apply button");
  setTimeout(disableApply, 200);


  // Set timeout
  setTimeout(enableApply, 5000);
}
