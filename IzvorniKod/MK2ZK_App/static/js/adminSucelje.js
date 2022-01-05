
// uredivanje informacija o predsjedavajucem

var userCollapse = document.getElementById("UserNameCollapse");
var bsUserCollapse = new bootstrap.Collapse(userCollapse, {toggle: false});
var fNameCollapse = document.getElementById("FNameCollapse");
var bsFNameCollapse = new bootstrap.Collapse(fNameCollapse, {toggle: false});
var lNameCollapse = document.getElementById("LNameCollapse");
var bsLNameCollapse = new bootstrap.Collapse(lNameCollapse, {toggle: false});
var emailCollapse = document.getElementById("EmailCollapse");
var bsEmailCollapse = new bootstrap.Collapse(emailCollapse, {toggle: false});

var user = document.getElementById("korisnickoIme");
userCollapse.addEventListener('show.bs.collapse', function(){
              user.style.position = "absolute";
              document.getElementById("UserNameDiv").style.paddingBottom = "0px";
            });
userCollapse.addEventListener('hidden.bs.collapse', function(){
              user.style.position = "relative";
              document.getElementById("UserNameDiv").style.paddingBottom = "9px";
            });

var fName = document.getElementById("ime");
fNameCollapse.addEventListener('show.bs.collapse', function(){
              fName.style.position = "absolute";
              document.getElementById("FNameDiv").style.paddingBottom = "0px";
            });
fNameCollapse.addEventListener('hidden.bs.collapse', function(){
              fName.style.position = "relative";
              document.getElementById("FNameDiv").style.paddingBottom = "9px";
            });

var lName = document.getElementById("prezime");
lNameCollapse.addEventListener('show.bs.collapse', function(){
              lName.style.position = "absolute";
              document.getElementById("LNameDiv").style.paddingBottom = "0px";
            });
lNameCollapse.addEventListener('hidden.bs.collapse', function(){
              lName.style.position = "relative";
              document.getElementById("LNameDiv").style.paddingBottom = "9px";
            });

var email = document.getElementById("email");
emailCollapse.addEventListener('show.bs.collapse', function(){
              email.style.position = "absolute";
              document.getElementById("EmailDiv").style.paddingBottom = "0px";
            });
emailCollapse.addEventListener('hidden.bs.collapse', function(){
              email.style.position = "relative";
              document.getElementById("EmailDiv").style.paddingBottom = "9px";
            });

window.onload = function(){
              //document.getElementById("NewUserNameForm").style.display = "none";
              //document.getElementById("NewFNameForm").style.display = "none";
              //document.getElementById("NewLNameForm").style.display = "none";
              //document.getElementById("NewEmailForm").style.display = "none";
            };
function UpdateUserName(){
              //document.getElementById("NewUserNameForm").style.display = "inline";
              document.getElementById("formUserNameChanges").style.display = "inline";
              document.getElementById("UpdateUserName").style.display = "none";

              userCollapse.style.position = "relative";
              bsUserCollapse.toggle();
            }
function UpdateFName(){
              //document.getElementById("NewFNameForm").style.display = "inline";
              document.getElementById("formFNameChanges").style.display = "inline";
              document.getElementById("UpdateFName").style.display = "none";
              
              fNameCollapse.style.position = "relative";
              bsFNameCollapse.toggle();
            }
function UpdateLName(){
              //document.getElementById("NewLNameForm").style.display = "inline";
              document.getElementById("formLNameChanges").style.display = "inline";
              document.getElementById("UpdateLName").style.display = "none";
              
              lNameCollapse.style.position = "relative";
              bsLNameCollapse.toggle();
            }
function UpdateEmail(){
              //document.getElementById("NewEmailForm").style.display = "inline";
              document.getElementById("formEmailChanges").style.display = "inline";
              document.getElementById("UpdateEmail").style.display = "none";
              
              emailCollapse.style.position = "relative";
              bsEmailCollapse.toggle();
            }
function CancelUpdateUsername(){
              //document.getElementById("NewUserNameForm").style.display = "none";
              document.getElementById("formUserNameChanges").style.display = "none";
              document.getElementById("UpdateUserName").style.display = "inline";
              document.getElementById("korisnickoIme").style.display="inline";
              bsUserCollapse.toggle();
            }
function CancelUpdateFName(){
              //document.getElementById("NewFNameForm").style.display = "none";
              document.getElementById("formFNameChanges").style.display = "none";
              document.getElementById("UpdateFName").style.display = "inline";
              document.getElementById("ime").style.display = "inline";
              bsFNameCollapse.toggle();
            }
function CancelUpdateLName(){
              //document.getElementById("NewLNameForm").style.display = "none";
              document.getElementById("formLNameChanges").style.display = "none";
              document.getElementById("UpdateLName").style.display = "inline";
              document.getElementById("prezime").style.display = "inline";
              bsLNameCollapse.toggle();
            }

            function CancelUpdateEmail(){
              //document.getElementById("NewEmailForm").style.display = "none";
              document.getElementById("formEmailChanges").style.display = "none";
              document.getElementById("UpdateEmail").style.display = "inline";
              document.getElementById("email").style.display = "inline";
              bsEmailCollapse.toggle();
            }