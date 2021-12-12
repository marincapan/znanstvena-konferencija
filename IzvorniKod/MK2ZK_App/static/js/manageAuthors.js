//funkcije za dodavanje i uklanjanje autora, za MojiRadovi i Signup
/**
 *Sluzi za dodavanje novih autora u listu autora pojedinog dokumenta.
 **/
function AddAuthor(){
    //prati broj autora (SO kaze da + cini ovo brojem)
    var brojAutora = +document.getElementById("brojAutora").value;

    //kloniramo prvog autora pa ga nastavljamo uredjivati
    var noviAutor = document.getElementById("autori").firstElementChild.cloneNode(true); 
    console.log(noviAutor);

    if(noviAutor.hasChildNodes()){
      var children = noviAutor.childNodes;

      //Prolazimo kroz svu djecu elementa
      for(var i = 0; i < children.length; i++){

        //Obrada za redni broj autora
        if(children[i].id == "authorsLabel"){
          children[i].innerText = (brojAutora+1) + ".";
          console.log("Tu sam");
          console.log(children[i]);
        }
        //Obrada za ID-eve imena i prezimena
        if(children[i].id == "autorIme"){
          for(var j = 0; j < children[i].childNodes.length; j++){
            if(children[i].childNodes[j].id == "autorFName0"){
              children[i].childNodes[j].id = "autorFName" + brojAutora;
              children[i].childNodes[j].name = "autorFName" + brojAutora;
              children[i].childNodes[j].value = "";
            }
            if(children[i].childNodes[j].id == "autorLName0"){
              children[i].childNodes[j].id = "autorLName" + brojAutora;
              children[i].childNodes[j].name = "autorLName" + brojAutora;
              children[i].childNodes[j].value = "";
            }
          }
        }

        //Obrada za ID-eve podataka o autoru
        if(children[i].id == "autorPodaci"){
          for(var j = 0; j < children[i].childNodes.length; j++){
            //Obrada za Email
            if(children[i].childNodes[j].id == "autorEmail0"){
              children[i].childNodes[j].id = "autorEmail" + brojAutora;
              children[i].childNodes[j].name = "autorEmail" + brojAutora;
              children[i].childNodes[j].value = "";
            }
            //Obrada za kontakt radio button
            if(children[i].childNodes[j].id == "autorPodaciKontakt"){
              for(var k = 0; k < children[i].childNodes[j].childNodes.length; k++){
                if(children[i].childNodes[j].childNodes[k].id == "autorKontakt0"){
                  children[i].childNodes[j].childNodes[k].id = "autorKontakt" + brojAutora;
                  children[i].childNodes[j].childNodes[k].checked = false; //Ako je prvi checkan i doda se novi vise novi nije checkan
                  //children[i].childNodes[j].childNodes[k].name = "autorKontakt" + brojAutora;
                }
                if(children[i].childNodes[j].childNodes[k].id == "autorKontaktLabel0"){
                  children[i].childNodes[j].childNodes[k].id = "autorKontaktLabel" + brojAutora;
                  children[i].childNodes[j].childNodes[k].htmlFor = "autorKontakt" + brojAutora;
                  console.log(children[i].childNodes[j].childNodes[k])
                }
              }
            }
          }
        }

      }
    }

    //Dodavanje novog autora kao child element u div s autorima
    document.getElementById("autori").appendChild(noviAutor);

    //Povecavanje brojaca
    document.getElementById("brojAutora").value = brojAutora + 1;

    if(brojAutora + 1 > 1){
      document.getElementById("btnMakniAutora").disabled = false;
    }
  }

function RemoveAuthor(){
    //prati broj autora (SO kaze da + cini ovo brojem)
    var brojAutora = +document.getElementById("brojAutora").value;

    //micemo zadnjeg dodanog autora
    document.getElementById("autori").removeChild(document.getElementById("autori").lastElementChild); 

    //Smanjivanje brojaca
    document.getElementById("brojAutora").value = brojAutora - 1;

    //Ako ima samo jedan autor zabrani brisanje
    if(brojAutora - 1 == 1){
      document.getElementById("btnMakniAutora").disabled = true;
    }
}

/*
            function AddField() {
              
              const num=document.getElementById("numOfAuthors").value;
              
              const inputime=document.getElementById("authorName").cloneNode();
              const inputimename=document.getElementById("authorName").getAttribute("name");
              const div1ime=document.getElementById("authordiv1");
              const div2ime=document.getElementById("authordiv2");
              const labelime=document.getElementById("authorNameLabel");

              const inputprezime=document.getElementById("authorLname").cloneNode();
              const div1prezime=document.getElementById("authordiv3");
              const labelprezime=document.getElementById("authorLnameLabel");
              const inputprezimename=document.getElementById("authorLname").getAttribute("name");
              
              const inputemail=document.getElementById("emailautora").cloneNode();
              const div1email=document.getElementById("authordiv4");
              const labelemail=document.getElementById("emailautorLabel");
              const inputemailname=document.getElementById("emailautora").getAttribute("name");
              
              

              const form=document.getElementById("autoridiv");
              for(let i=0;i<num-1;i++){
                div2ime.appendChild(labelime.cloneNode());
                const newName=inputimename + String(i+2)
                inputime.setAttribute("name",newName)
                inputime.setAttribute("id",newName)
                div2ime.appendChild(inputime.cloneNode());
                div1ime.appendChild(div2ime.cloneNode());

                div1prezime.appendChild(labelprezime.cloneNode());
                const newLName=inputprezimename + String(i+2)
                inputprezime.setAttribute("name",newLName)
                inputprezime.setAttribute("id",newLName)
                div1prezime.appendChild(inputprezime.cloneNode());

                div1email.appendChild(labelemail.cloneNode());
                const newEmail=inputemailname + String(i+2)
                inputemail.setAttribute("name",newEmail)
                inputemail.setAttribute("id",newEmail)
                div1email.appendChild(inputemail.cloneNode());

                form.appendChild(div1ime.cloneNode());
                form.appendChild(div1prezime.cloneNode());
                form.appendChild(div1ime.cloneNode());
              }
            }
            */