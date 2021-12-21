// za azuriranje info stranice, funkcionalnost gumba

window.onload = function() {
    document.getElementById("update-card").style.display = "none";
};

function OpenPopup() {
    document.getElementById("update-card").style.display = "block";
    document.getElementById("editedText").value = document.getElementById("infoId").innerText;
}

function ClosePopup() {
    document.getElementById("update-card").style.display = "none";
}

function UpdateContent() {
    document.getElementById("infoId").innerHTML = document.getElementById("editedText").value;
    ClosePopup();
}