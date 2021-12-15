//za azuriranje Info stranice, odn O konferenciji (moze samo Admin)

var titleCollapse = document.getElementById("titleCollapse");
//var bsTitleCollapse = new bootstrap.Collapse(titleCollapse, {toggle: false});

var title = document.getElementById("myTitle");
/*titleCollapse.addEventListener('show.bs.collapse', function(){
              user.style.position = "absolute";
              document.getElementById("titleDiv").style.paddingBottom = "0px";
            });
titleCollapse.addEventListener('hidden.bs.collapse', function(){
              user.style.position = "relative";
              document.getElementById("titleDiv").style.paddingBottom = "9px";
            });*/

function UpdateTitle(){
    //document.getElementById("NewUserNameForm").style.display = "inline";
    document.getElementById("formTitleChange").style.display = "inline";
    document.getElementById("UpdateTitle").style.display = "none";

    titleCollapse.style.position = "relative";
    
    //bsTitleCollapse.toggle();
}

function CancelTitle(){
    //document.getElementById("NewUserNameForm").style.display = "none";
    document.getElementById("formTitleChange").style.display = "none";
    document.getElementById("UpdateTitle").style.display = "inline";
    //bsTitleCollapse.toggle();
}

var Naziv = document.getElementById("naziv");
var NazivCollapse = document.getElementById("NazivCollapse");
var bsNazivCollapse = new bootstrap.Collapse(NazivCollapse, {toggle: false});

NazivCollapse.addEventListener('show.bs.collapse', function(){
              Naziv.style.position = "absolute";
              document.getElementById("NazivDiv").style.paddingBottom = "0px";
            });
NazivCollapse.addEventListener('hidden.bs.collapse', function(){
              Naziv.style.position = "relative";
              document.getElementById("NazivDiv").style.paddingBottom = "9px";
            });
function UpdateNaziv(){
//document.getElementById("NewNazivForm").style.display = "inline";
document.getElementById("formNazivChanges").style.display = "inline";
document.getElementById("UpdateNaziv").style.display = "none";
              
NazivCollapse.style.position = "relative";
bsNazivCollapse.toggle();
}
function CancelUpdateNaziv(){
  //document.getElementById("NewNazivForm").style.display = "none";
  document.getElementById("formNazivChanges").style.display = "none";
  document.getElementById("UpdateNaziv").style.display = "inline";
  document.getElementById("naziv").style.display = "inline";
  bsNazivCollapse.toggle();
}


var Opis = document.getElementById("opis");
var OpisCollapse = document.getElementById("OpisCollapse");
var bsOpisCollapse = new bootstrap.Collapse(OpisCollapse, {toggle: false});

OpisCollapse.addEventListener('show.bs.collapse', function(){
              Opis.style.position = "absolute";
              document.getElementById("OpisDiv").style.paddingBottom = "0px";
            });
OpisCollapse.addEventListener('hidden.bs.collapse', function(){
              Opis.style.position = "relative";
              document.getElementById("OpisDiv").style.paddingBottom = "9px";
            });
function UpdateOpis(){
document.getElementById("opis").style.display = "none";
document.getElementById("formOpisChanges").style.display = "inline";
document.getElementById("UpdateOpis").style.display = "none";
              
OpisCollapse.style.position = "relative";
bsOpisCollapse.toggle();
}
function CancelUpdateOpis(){
  //document.getElementById("NewOpisForm").style.display = "none";
  document.getElementById("formOpisChanges").style.display = "none";
  document.getElementById("UpdateOpis").style.display = "inline";
  document.getElementById("opis").style.display = "inline";
  bsOpisCollapse.toggle();
}
var Datum = document.getElementById("datum");
var DatumCollapse = document.getElementById("DatumCollapse");
var bsDatumCollapse = new bootstrap.Collapse(DatumCollapse, {toggle: false});

DatumCollapse.addEventListener('show.bs.collapse', function(){
              Datum.style.position = "absolute";
              document.getElementById("DatumDiv").style.paddingBottom = "0px";
            });
DatumCollapse.addEventListener('hidden.bs.collapse', function(){
              Datum.style.position = "relative";
              document.getElementById("DatumDiv").style.paddingBottom = "9px";
            });
function UpdateDatum(){

document.getElementById("formDatumChanges").style.display = "inline";
document.getElementById("UpdateDatum").style.display = "none";
              
DatumCollapse.style.position = "relative";
bsDatumCollapse.toggle();
}
function CancelUpdateDatum(){
  //document.getElementById("NewDatumForm").style.display = "none";
  document.getElementById("formDatumChanges").style.display = "none";
  document.getElementById("UpdateDatum").style.display = "inline";
  document.getElementById("Datum").style.display = "inline";
  bsDatumCollapse.toggle();
}
var RokPocPrijava = document.getElementById("RokPocPrijava");
var RokPocPrijavaCollapse = document.getElementById("RokPocPrijavaCollapse");
var bsRokPocPrijavaCollapse = new bootstrap.Collapse(RokPocPrijavaCollapse, {toggle: false});

RokPocPrijavaCollapse.addEventListener('show.bs.collapse', function(){
              RokPocPrijava.style.position = "absolute";
              document.getElementById("RokPocPrijavaDiv").style.paddingBottom = "0px";
            });
RokPocPrijavaCollapse.addEventListener('hidden.bs.collapse', function(){
              RokPocPrijava.style.position = "relative";
              document.getElementById("RokPocPrijavaDiv").style.paddingBottom = "9px";
            });
function UpdateRokPocPrijava(){

document.getElementById("formRokPocPrijavaChanges").style.display = "inline";
document.getElementById("UpdateRokPocPrijava").style.display = "none";
              
RokPocPrijavaCollapse.style.position = "relative";
bsRokPocPrijavaCollapse.toggle();
}
function CancelUpdateRokPocPrijava(){
  //document.getElementById("NewRokPocPrijavaForm").style.display = "none";
  document.getElementById("formRokPocPrijavaChanges").style.display = "none";
  document.getElementById("UpdateRokPocPrijava").style.display = "inline";
  document.getElementById("RokPocPrijava").style.display = "inline";
  bsRokPocPrijavaCollapse.toggle();
}

var RokPrijava = document.getElementById("RokPrijava");
var RokPrijavaCollapse = document.getElementById("RokPrijavaCollapse");
var bsRokPrijavaCollapse = new bootstrap.Collapse(RokPrijavaCollapse, {toggle: false});

RokPrijavaCollapse.addEventListener('show.bs.collapse', function(){
              RokPrijava.style.position = "absolute";
              document.getElementById("RokPrijavaDiv").style.paddingBottom = "0px";
            });
RokPrijavaCollapse.addEventListener('hidden.bs.collapse', function(){
              RokPrijava.style.position = "relative";
              document.getElementById("RokPrijavaDiv").style.paddingBottom = "9px";
            });
function UpdateRokPrijava(){

document.getElementById("formRokPrijavaChanges").style.display = "inline";
document.getElementById("UpdateRokPrijava").style.display = "none";
              
RokPrijavaCollapse.style.position = "relative";
bsRokPrijavaCollapse.toggle();
}
function CancelUpdateRokPrijava(){
  //document.getElementById("NewRokPrijavaForm").style.display = "none";
  document.getElementById("formRokPrijavaChanges").style.display = "none";
  document.getElementById("UpdateRokPrijava").style.display = "inline";
  document.getElementById("RokPrijava").style.display = "inline";
  bsRokPrijavaCollapse.toggle();
}

var RokPocRecenzija= document.getElementById("RokPocRecenzija");
var RokPocRecenzijaCollapse = document.getElementById("RokPocRecenzijaCollapse");
var bsRokPocRecenzijaCollapse = new bootstrap.Collapse(RokPocRecenzijaCollapse, {toggle: false});

RokPocRecenzijaCollapse.addEventListener('show.bs.collapse', function(){
              RokPocRecenzija.style.position = "absolute";
              document.getElementById("RokPocRecenzijaDiv").style.paddingBottom = "0px";
            });
RokPocRecenzijaCollapse.addEventListener('hidden.bs.collapse', function(){
              RokPocRecenzija.style.position = "relative";
              document.getElementById("RokPocRecenzijaDiv").style.paddingBottom = "9px";
            });
function UpdateRokPocRecenzija(){

document.getElementById("formRokPocRecenzijaChanges").style.display = "inline";
document.getElementById("UpdateRokPocRecenzija").style.display = "none";
              
RokPocRecenzijaCollapse.style.position = "relative";
bsRokPocRecenzijaCollapse.toggle();
}
function CancelUpdateRokPocRecenzija(){
  //document.getElementById("NewRokPocRecenzijaForm").style.display = "none";
  document.getElementById("formRokPocRecenzijaChanges").style.display = "none";
  document.getElementById("UpdateRokPocRecenzija").style.display = "inline";
  document.getElementById("RokPocRecenzija").style.display = "inline";
  bsRokPocRecenzijaCollapse.toggle();
}
var RokRecenzenti= document.getElementById("RokRecenzenti");
var RokRecenzentiCollapse = document.getElementById("RokRecenzentiCollapse");
var bsRokRecenzentiCollapse = new bootstrap.Collapse(RokRecenzentiCollapse, {toggle: false});

RokRecenzentiCollapse.addEventListener('show.bs.collapse', function(){
              RokRecenzenti.style.position = "absolute";
              document.getElementById("RokRecenzentiDiv").style.paddingBottom = "0px";
            });
RokRecenzentiCollapse.addEventListener('hidden.bs.collapse', function(){
              RokRecenzenti.style.position = "relative";
              document.getElementById("RokRecenzentiDiv").style.paddingBottom = "9px";
            });
function UpdateRokRecenzenti(){

document.getElementById("formRokRecenzentiChanges").style.display = "inline";
document.getElementById("UpdateRokRecenzenti").style.display = "none";
              
RokRecenzentiCollapse.style.position = "relative";
bsRokRecenzentiCollapse.toggle();
}
function CancelUpdateRokRecenzenti(){
  //document.getElementById("NewRokRecenzentiForm").style.display = "none";
  document.getElementById("formRokRecenzentiChanges").style.display = "none";
  document.getElementById("UpdateRokRecenzenti").style.display = "inline";
  document.getElementById("RokRecenzenti").style.display = "inline";
  bsRokRecenzentiCollapse.toggle();
}
var RokAdmin= document.getElementById("RokAdmin");
var RokAdminCollapse = document.getElementById("RokAdminCollapse");
var bsRokAdminCollapse = new bootstrap.Collapse(RokAdminCollapse, {toggle: false});

RokAdminCollapse.addEventListener('show.bs.collapse', function(){
              RokAdmin.style.position = "absolute";
              document.getElementById("RokAdminDiv").style.paddingBottom = "0px";
            });
RokAdminCollapse.addEventListener('hidden.bs.collapse', function(){
              RokAdmin.style.position = "relative";
              document.getElementById("RokAdminDiv").style.paddingBottom = "9px";
            });
function UpdateRokAdmin(){

document.getElementById("formRokAdminChanges").style.display = "inline";
document.getElementById("UpdateRokAdmin").style.display = "none";
              
RokAdminCollapse.style.position = "relative";
bsRokAdminCollapse.toggle();
}
function CancelUpdateRokAdmin(){
  //document.getElementById("NewRokAdminForm").style.display = "none";
  document.getElementById("formRokAdminChanges").style.display = "none";
  document.getElementById("UpdateRokAdmin").style.display = "inline";
  document.getElementById("RokAdmin").style.display = "inline";
  bsRokAdminCollapse.toggle();
}