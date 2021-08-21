M.AutoInit();

var slider = document.getElementById('date-slider');
noUiSlider.create(slider, {
 start: [2001, 2020],
 connect: true,
 step: 1,
 orientation: 'horizontal', // 'horizontal' or 'vertical'
 range: {
   'min': 2001,
   'max': 2020
 },
 format: wNumb({
   decimals: 0
 })
});
