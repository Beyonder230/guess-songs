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

function openCustom() {
    if (document.getElementById("custom").style.display != "block") {
        document.getElementById("custom").style.display = "block";
    } else {
        document.getElementById("custom").style.display = "none";
    }
}

function closeCustom() {
    document.getElementById("custom").style.display = "none";
}