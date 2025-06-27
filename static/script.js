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

function customValidation() {
    const url = document.getElementById("url").value;

    const spotify = "spotify";
    const deezer = "deezer";

    let platIsValid = false;
    let deezerCount = 0;
    let spotifyCount = 0;

    const playlist = "playlist";
    const album = "album";

    let typeIsValid = false;
    let playlistCount = 0;
    let albumCount = 0;

    for (let char = 0; char < url.length; char++) {
        // spotify validation
        if (url[char] == spotify[spotifyCount]) {
            spotifyCount += 1;

            if (spotifyCount == spotify.length) {
                platIsValid = true;
            }
        } else {
            spotifyCount = 0;
        }

        // deezer validation
        if (url[char] == deezer[deezerCount]) {
            deezerCount += 1;

            if (deezerCount == deezer.length) {
                platIsValid = true;
            }
        } else {
            deezerCount = 0;
        }


        // playlist validation
        if (url[char] == playlist[playlistCount]) {
            playlistCount += 1;

            if (playlistCount == playlist.length) {
                typeIsValid = true;
            }
        } else {
            playlistCount = 0;
        }

        // album validation
        if (url[char] == album[albumCount]) {
            albumCount += 1;

            if (albumCount == album.length) {
                typeIsValid = true;
            }
        } else {
            albumCount = 0;
        }
    }

    if (platIsValid == false || typeIsValid == false) {
        alert("Not valid URL!!!\nPlease select a valid playlist/album link from spotify or deezer, look for share and copy link option.");
        return false;
    } else {
        customGameLoading();
    }
}

function customGameLoading() {
    const loadings = document.getElementsByClassName("spinner-border");
    if (loadings.length < 1) {
        const newDiv = document.createElement("div");
        newDiv.classList.add("spinner-border", "text-success", "d-flex", "justify-content-center", "m-3");
        newDiv.role = "status";

        const newSpan = document.createElement("span");
        newSpan.classList.add("visually-hidden");
        newSpan.innerHTML = "Loading...";

        newDiv.appendChild(newSpan);

        const loadingForm = document.getElementById("loading");
        loadingForm.appendChild(newDiv);
    }
}