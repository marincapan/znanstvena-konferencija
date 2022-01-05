// Set the date we're counting down to
var datum = document.getElementById("rokPrijave").value

//pocetne vrijednosti
document.getElementById("countdown-days").innerHTML = 0;
document.getElementById("countdown-hours").innerHTML = 0;
document.getElementById("countdown-minutes").innerHTML = 0;
document.getElementById("countdown-seconds").innerHTML = 0;

if (datum != "Nedefiniran datum"){
    
  datum = datum.replace(".","")
  datum = datum.replace(",","")
  
var datum = new Date(datum).getTime();

// print(datum)
// var datum = new Date("Jan 5, 2022 15:37:25").getTime();

// beginning numbers
document.getElementById("countdown-days").innerHTML = 0;
document.getElementById("countdown-hours").innerHTML = 0;
document.getElementById("countdown-minutes").innerHTML = 0;
document.getElementById("countdown-seconds").innerHTML = 0;

// Update the count down every 1 second
var x = setInterval(function() {

// Get today's date and time
var now = new Date().getTime();

// Find the distance between now and the count down date
var distance = datum - now;

// Time calculations for days, hours, minutes and seconds
var days = Math.floor(distance / (1000 * 60 * 60 * 24));
var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
var seconds = Math.floor((distance % (1000 * 60)) / 1000);

// Display the result in the element with ids
document.getElementById("countdown-days").innerHTML = days;
document.getElementById("countdown-hours").innerHTML = hours;
document.getElementById("countdown-minutes").innerHTML = minutes;
document.getElementById("countdown-seconds").innerHTML = seconds;

// If the count down is finished, write some text
if (distance < 0) {
  clearInterval(x);
  document.getElementById("rok").innerHTML = "Rok je istekao."; //definirati opsirniju poruku po potrebi
  document.getElementById("countdownid").style.display = "none";
}
}, 1000);
}



