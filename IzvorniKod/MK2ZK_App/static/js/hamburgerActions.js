//Javascript za hamburger animacije za SVAKI html

var navbarCollapse = document.getElementById("navbarContent");
            
navbarCollapse.addEventListener('show.bs.collapse', function(){
          document.getElementById("navbarTogglerIcon").style.animation="rotation 0.5s both";
        });
navbarCollapse.addEventListener('shown.bs.collapse', function(){
          document.getElementById("navbarTogglerIcon").style.animation="none";
          document.getElementById("navbarTogglerIcon").style.transform="rotate(90deg)";
        });
navbarCollapse.addEventListener('hide.bs.collapse', function(){
          document.getElementById("navbarTogglerIcon").style.animation="rotation 0.35s reverse";
        });
navbarCollapse.addEventListener('hidden.bs.collapse', function(){
          document.getElementById("navbarTogglerIcon").style.animation="none";
          document.getElementById("navbarTogglerIcon").style.transform="rotate(0deg)";
        });