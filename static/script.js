function openConfig() {
    const settings = document.getElementById("settings");

    if (settings.classList.contains("active")) {
        settings.classList.remove("active");
        document.getElementById("page-overlay").classList.remove("active");
    } else {
        settings.classList.add("active");
        document.getElementById("page-overlay").classList.add("active");
    }
}

function closeConfig() {
    document.getElementById("settings").classList.remove("active");
    document.getElementById("page-overlay").classList.remove("active");
}

function openCustom() {
    const customForm = document.getElementById("custom");

    if (customForm.classList.contains("active")) {
        customForm.classList.remove("active");
        document.getElementById("page-overlay").classList.remove("active");
    } else {
        customForm.classList.add("active");
        document.getElementById("page-overlay").classList.add("active");
    }
}

function closeCustom() {
    document.getElementById("custom").classList.remove("active");
    document.getElementById("page-overlay").classList.remove("active");
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
    document.getElementById("custom_game_button").classList.add("disabled");

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
let correctAnswerId;
let playableTracksSize;
let score;
const time = document.getElementById("game-container").dataset.time;

async function startGame() {
    initializeAudioPlayer();
    var data = await getData();
    if (data) {
        setData(data);
    }
}

function initializeAudioPlayer() {
    const audio = document.getElementById("song");
    const playPauseBtn = document.getElementById("play-pause-btn");
    const seekBar = document.getElementById("seek-bar");
    const currentTimeDisplay = document.getElementById("current-time-display");
    const durationDisplay = document.getElementById("duration-display");
    const volumeBar = document.getElementById("volume-bar");

    if (!audio || !volumeBar) return;

    audio.volume = volumeBar.value / 100;

    volumeBar.addEventListener("input", () => {
        audio.volume = volumeBar.value / 100;
    });

    playPauseBtn.addEventListener("click", () => {
        if (audio.paused) {
            playPauseBtn.textContent = "❚❚";
            audio.play();
        }
        else {
            playPauseBtn.textContent = '▶';
            audio.pause();
        }
    });

    audio.addEventListener("timeupdate", () => {
        seekBar.value = audio.currentTime;
        currentTimeDisplay.textContent = formatTime(audio.currentTime);

        const progressPercentage = (audio.currentTime / audio.duration) * 100;
        seekBar.style.setProperty('--seek-before-width', `${progressPercentage}%`);
    });

    audio.addEventListener("loadedmetadata", () => {
        seekBar.max = audio.duration;
        durationDisplay.textContent = formatTime(audio.duration);
    });

    audio.addEventListener("ended", () => {
        playPauseBtn.textContent = '▶';
    });

    seekBar.addEventListener("input", () => {
        audio.currentTime = seekBar.value;
        currentTimeDisplay.textContent = formatTime(seekBar.value);
    });

    audio.addEventListener("play", () => {
        if (played === false) {
            played = true;
            startCountdown(time);
        }
    });2
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const scds = Math.floor(seconds % 60);
    return `${minutes}:${scds.toString().padStart(2, '0')}`;
}

function gameWin() {
    const endgameDiv = document.getElementById("endgame");
    const message = document.getElementById("endgame_message");
    const icon = document.getElementById("endgame_icon");
    const stats = document.getElementById('endgame_stats');

    endgameDiv.classList.remove('victory', 'defeat');

    message.innerText = "you won!".toUpperCase();
    endgameDiv.classList.add("victory");
    icon.className = "fa-solid fa-trophy";
    stats.textContent = `Your score: ${score}/${score}`;

    document.getElementById("endgame").classList.add("active");
    document.getElementById("page-overlay").classList.add("active");
}

function gameLose() {
    const endgameDiv = document.getElementById("endgame");
    const message = document.getElementById("endgame_message");
    const icon = document.getElementById("endgame_icon");
    const stats = document.getElementById('endgame_stats');

    endgameDiv.classList.remove('victory', 'defeat');

    message.innerText = "you lost!".toUpperCase();
    endgameDiv.classList.add("defeat");
    icon.className = "fa-solid fa-face-sad-tear";
    stats.textContent = `Your score: ${score}/${score + playableTracksSize}`;


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

function preLoadAsset(url) {
    return new Promise((resolve, reject) => {
        const isImage = /\.(jpeg|jpg|gif|png|webp)$/.test(url);

        if (isImage) {
            const img = new Image();

            img.onload = () => resolve(url);
            img.onerror = () => reject(new Error(`Error at loading image: ${url}`));

            img.src = url;
        } else {
            resolve(url);
        }
    });
}

async function getData() {
    try {
        console.log("1. Fetching next round data...");
        const response = await fetch("/get_game_data");

        if (!response.ok)
            throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        console.log("2. Data received from backend:", data);

        if (data.error)
            throw new Error(`Server data error: ${data.error}`);

        if (!data.win) {
            playableTracksSize = data.playable_tracks_size;

            const urlsToPreload = [...data.options.map(option => option.image)];
            console.log("3. Assets to preload:", urlsToPreload);

            if (!data.song.preview) {
                console.error("CRITICAL ERROR: The received song has no preview URL!");
                throw new Error("Song without preview received from backend.");
            }

            const preloadPromises = urlsToPreload.map(url => preLoadAsset(url));

            console.log("4. Awaiting all assets to preload...");
            await Promise.all(preloadPromises);

            console.log("5. SUCCESS! All assets have been preloaded.");
        }

        return data;
        
    } catch (error) {
        console.error("ERROR: Failed inside getGame's try-catch block:", error);
        alert("Could not load the page! Please try to reload the page.");
    }
}

async function setData(data) {
    if (data.win === true)
        return gameWin();

    // AUDIO
    const audio = document.getElementById("song");
    const audio_source = document.getElementById("song_source");

    if (data.song && data.song.preview) {
        audio_source.src = data.song.preview;
        audio.load();
    } else {
        showTemporaryMessage("Unable to load this song, skipping...");
        const nextRoundDataPromise = getData();
        setTimeout(async () => {
            data = await nextRoundDataPromise;
            if (data) {
                next_round(data);
            }
        }, 2000);
    }


    // OPTIONS
    const options = document.querySelectorAll(".option-button");

    options.forEach((container, index) => {
        const optionData = data.options[index];

        if (optionData) {
            const image = container.querySelector(".img-answer");
            const title = container.querySelector('p');

            image.src = optionData.image || "/static/default_cover.png";
            title.textContent = optionData.title;

            container.dataset.songId = optionData.id;
            image.dataset.songId = optionData.id;
        } else {
            container.style.display = "none";
        }
    });

    correctAnswerId = data.song.id;
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

    const rightAnswerSound = document.getElementById("right_answer_sound");
    const wrongAnswerSound = document.getElementById("wrong_answer_sound");
    answered = true;
    object.classList.add("selected");

    const gamemode = document.getElementById("game-container").dataset.gamemode;
    const body = { selected_id: object.dataset.songId, gamemode: gamemode, correct_id: correctAnswerId };
    
    try {
        const response = await fetch("/check_answer", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error("Error at checking answer");
        }

        clearInterval(countdownInterval);
        const resultData = await response.json();

        const current_score = document.getElementById("current_score");
        score = resultData.score;
        current_score.innerHTML = score.toString();
        const max_score = document.getElementById("biggest_score");
        max_score.innerHTML = resultData.max_score.toString();

        mark_answers(resultData.correct_song_id);
        show_title(resultData.correct_song_id);

        if (resultData.result === "correct") {
            var nextRoundDataPromise = getData();
            if (rightAnswerSound) {
                rightAnswerSound.currentTime = 0;
                rightAnswerSound.play();
            }
            setTimeout(async () => {
                const data = await nextRoundDataPromise;
                if (data) {
                    next_round(data);
                }
            }, 2000);
        } else {
            if (wrongAnswerSound) {
                wrongAnswerSound.currentTime = 0;
                wrongAnswerSound.play();
            }
            setTimeout(function () {
                gameLose();
            }, 2000);
        }
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

function next_round(data) {
    const play_pause_btn = document.getElementById("play-pause-btn");
    play_pause_btn.textContent = '▶';

    clear_marks();
    clear_title();
    clear_selected();

    const time = document.getElementById("game-container").dataset.time;
    reset_countdown(time);

    played = false;
    answered = false;
    setData(data);
}

function showTemporaryMessage(text) {
    const messageElement = document.getElementById("game-message-area");
    if (messageElement) {
        messageElement.textContent = text;
        messageElement.style.display = 'block';
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 2000);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const gameContainer = document.getElementById("game-container");

    if (gameContainer) {
        startGame();
    }
});