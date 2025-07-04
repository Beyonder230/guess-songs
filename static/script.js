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

// MAIN GAME LOGIC ================================================================================================================================================================
let played = false;
let countdownInterval;
let answered = false;

function startGame(time) {
    getData();

    document.getElementById("song").addEventListener('play', () => {
        if (played === false) {
            played = true;
            startCountdown(time);
        }
    });
}

function gameWin() {
    const message = document.getElementById("endgame_message");
    message.innerText = "you won!".toUpperCase();
    message.style.color = "green";

    // document.getElementById("endgame").style.display = "block";
    document.getElementById("endgame").classList.add("active");
    document.getElementById("page-overlay").classList.add("active");
}

function gameLose() {
    const message = document.getElementById("endgame_message");
    message.innerText = "you lost!".toUpperCase();
    message.style.color = "red";

    // document.getElementById("endgame").style.display = "block";
    document.getElementById("endgame").classList.add("active");
    document.getElementById("page-overlay").classList.add("active");
}

function reset_countdown(time) {
    clearInterval(countdownInterval);
    let timer = document.getElementById("time");
    
    if (timer) {
        timer.innerText = time.toString();
    }
}

function clear_marks() {
    const marks = document.querySelectorAll(".img-check");

    if (marks) {
        marks.forEach((mark) => {
            mark.remove();
        });
    }
}

async function getData() {
    try {
        const response = await fetch("/get_game_data");

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(`Server data error: ${data.error}`);
        }

        if (data.win === true) {
            gameWin();
        } else {
            setData(data);
        }
 
    } catch (error) {
        console.log("Error at setting the game.");
        alert("Could not load the page! Please try to reload the page.");
    }
}

function setData(data) {
    // AUDIO
    const audio = document.getElementById("song");
    const audio_source = document.getElementById("song_source");
    audio_source.src = data.song.preview;
    audio.load();

    // OPTIONS
    const options = document.querySelectorAll(".option-button");

    options.forEach((container, index) => {
        const optionData = data.options[index];

        if (optionData) {
            const image = container.querySelector(".img-answer");
            const title = container.querySelector('p');

            image.src = optionData.image || '';
            title.textContent = optionData.title;

            container.dataset.songId = optionData.id;
            image.dataset.songId = optionData.id;
        } else {
            container.style.display = "none";
        }
    });
}

function startCountdown(time) {
    let timer = document.getElementById("time");

    clearInterval(countdownInterval);

    const updateTimerDisplay = () => {
        if (timer) {
            timer.innerText = time.toString();
        }
    };

    updateTimerDisplay();

    countdownInterval = setInterval(function () {
        time--;
        updateTimerDisplay();

        if (time <= 0) {
            clearInterval(countdownInterval);
            gameLose();
            return;
        }
    }, 1000);
}

function show_title(correct_song_id) {
    const question_marks = document.getElementById("questions");
    const correctContainer = document.querySelector(`.option-button [data-song-id="${correct_song_id}"]`);

    if (correctContainer) {
        const title = correctContainer.closest(".option-button").querySelector('p');
        question_marks.innerText = title.innerText;
    }
}

function clear_title() {
    const question_marks = document.getElementById("questions");
    question_marks.innerText = "???";
}

function mark_answers(correct_song_id) {
    const option_buttons = document.querySelectorAll(".option-button");

    option_buttons.forEach((option_button) => {
        const check_image = document.createElement("img");
        check_image.classList.add("img-check");
        
        if (option_button.dataset.songId == correct_song_id) {
            check_image.src = "/static/check.png";
        } else {
            check_image.src = "/static/delete.png";
        }

        const image_container = option_button.querySelector("div");
        image_container.appendChild(check_image);
    });
}

async function check_answer(object) {
    if (answered) {
        return
    }

    answered = true;
    object.classList.add("selected");

    const gamemode = document.getElementById("game-container").dataset.gamemode;
    const option_id = { id: object.dataset.songId, gamemode: gamemode };
    
    try {
        const response = await fetch("/check_answer", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify(option_id)
        });

        if (!response.ok) {
            throw new Error("Error at checking answer");
        }

        clearInterval(countdownInterval);
        const resultData = await response.json();

        const current_score = document.getElementById("current_score");
        current_score.innerHTML = resultData.score.toString();
        const max_score = document.getElementById("biggest_score");
        max_score.innerHTML = resultData.max_score.toString();

        mark_answers(resultData.correct_song_id);
        show_title(resultData.correct_song_id);

        setTimeout(function () {
            if (resultData.result === "correct") {
                next_round();
            } else {
                gameLose();
            }
         }, 2000);
    } catch (error) {
        console.log("Error at checking answer:", error);
        answered = false;
    }
}

function clear_selected() {
    const selected = document.querySelectorAll(".selected");

    selected.forEach(item => {
        item.classList.remove("selected");
    });
}

function next_round() {
    clear_marks();
    clear_title();
    clear_selected();

    const time = document.getElementById("game-container").dataset.time;
    reset_countdown(time);

    played = false;
    answered = false;
    getData();
}

document.addEventListener("DOMContentLoaded", () => {
    const gameContainer = document.getElementById("game-container");

    if (gameContainer) {
        const time = gameContainer.dataset.time;
        startGame(time);
    }
});