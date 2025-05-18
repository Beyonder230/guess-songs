function openConfig() {
    if (document.getElementById("settings").style.display != "block") {
        document.getElementById("settings").style.display = "block";
    } else {
        document.getElementById("settings").style.display = "none";
    }
}

function closeConfig() {
    document.getElementById("settings").style.display = "none";
}