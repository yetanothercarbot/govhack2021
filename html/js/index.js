// Don't allow the year stop to be larger than year start
function updateYearBounds() {
  document.getElementById("dateMin").max = document.getElementById("dateMax").value;
  document.getElementById("dateMax").min = document.getElementById("dateMin").value;
}

document.getElementById("dateMax").addEventListener("change", updateYearBounds);
document.getElementById("dateMin").addEventListener("change", updateYearBounds);
