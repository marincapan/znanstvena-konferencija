window.onload = function(){
    /*
      document.getElementById("title").style.display = "none";
      document.getElementById("section").style.display = "none";
      document.getElementById("titleLabel").style.display = "none";
      document.getElementById("sectionLabel").style.display = "none";

      ////////IDS: numOfAuthorsLabel, numOfAuthors, btnOK, authorNameLabel,
      //authorName, authorLnameLabel, authorLname, emailConLabel, emailCon
      document.getElementById("numOfAuthorsLabel").style.display = "none";
      document.getElementById("numOfAuthors").style.display = "none";
      document.getElementById("btnOK").style.display = "none";
      document.getElementById("authorNameLabel").style.display = "none";
      document.getElementById("authorName").style.display = "none";
      document.getElementById("authorLnameLabel").style.display = "none";
      document.getElementById("authorLname").style.display = "none";
      document.getElementById("emailConLabel").style.display = "none";
      document.getElementById("emailCon").style.display = "none";*/

      //U pocetku ima samo jedan autor tako da ga se ne smije micati
      document.getElementById("btnMakniAutora").disabled = true;
  };
  function UpdateOnSudionik(){
    document.getElementById("title").disabled = false;
    document.getElementById("autorFName0").disabled = false;
    document.getElementById("autorLName0").disabled = false;
    document.getElementById("autorEmail0").disabled = false;
    document.getElementById("autorKontakt0").disabled = false;

    document.getElementById("stvariZaSudionika").style.display = "inline";
    }
  function UpdateOnRecezent(){
    document.getElementById("stvariZaSudionika").style.display = "none";
      
    document.getElementById("title").disabled = true;
    document.getElementById("autorFName0").disabled = true;
    document.getElementById("autorLName0").disabled = true;
    document.getElementById("autorEmail0").disabled = true;
    document.getElementById("autorKontakt0").disabled = true;
  }


  