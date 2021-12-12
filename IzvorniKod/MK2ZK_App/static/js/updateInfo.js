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