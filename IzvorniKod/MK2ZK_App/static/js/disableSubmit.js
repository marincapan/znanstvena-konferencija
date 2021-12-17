//ako ne odabre dokument ne smije submitat

files = document.querySelectorAll("input[type=file]");
for (let i = 0; i < files.length; i++){
    klasa = files[i].classList[1]
    console.log(klasa)
    
   
    if (files[i].files.length == 0 ){
        console.log("help")
            button = document.getElementById(klasa)
            button.disabled = true;
            greska = document.getElementById("greska"+klasa)
            if (greska){
                greska.innerHTML = "Učitajte rad prije predaje."
            }
           
            
        } else {
            console.log("help2")
            button = document.getElementById(klasa)
            button.disabled = false;
        }

    }

      

        
     
