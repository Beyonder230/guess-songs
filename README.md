<div align="right">
    <a href="./README-pt.md">🇧🇷 Read in Portuguese</a>
</div>

<div align="center">
  <img src="./static/logo.png" alt="Guess Songs Logo" width="200"/>
  <h1>Guess Songs!</h1>
</div>

<p align="center">
  A dynamic, web-based music quiz game designed to test your musical knowledge against the clock.
  <br />
  <a href="#key-features"><strong>Explore the Features »</strong></a>
  <br />
  <br />
  </p>

---

## About The Project

Guess Songs is a full-stack web application that challenges players to identify a song from a short audio preview. It features a robust backend built with Python and Flask that fetches and processes track data from major streaming platforms, and a dynamic, responsive frontend built with JavaScript that ensures a smooth and interactive gameplay experience.

The project handles complex data integration challenges, including a fuzzy-matching fallback system to find playable previews and a multi-level caching system for high performance.

<a name="key-features"></a>
### ✨ Key Features

- **Two Game Modes:**
    - **Singleplayer:** A quick-play mode with a curated default playlist.
    - **Custom Mode:** Allows users to play using any public Spotify or Deezer playlist or album URL and set a custom timer.
- **Dynamic Preview Fetching:** If a track from Spotify lacks a preview, the application intelligently searches for a playable version on the Deezer API using a sophisticated fuzzy matching algorithm.
- **High-Performance Caching:** Implements a multi-level server-side cache to store Spotify access tokens, individual Deezer API lookups, and fully processed playlists, drastically reducing load times on subsequent requests.
- **Custom Audio Player:** A fully custom-built HTML, CSS, and JavaScript audio player for a unique and polished user interface with smooth animations.
- **Responsive Design:** The interface is fully responsive and optimized for a great experience on both desktop and mobile devices.

### 🖼️ Screenshots

<p align="center">
  <img src="./static/screenshots/game-screen.png" alt="Game Screen" width="80%">
  <br>
  <em>The main game interface during a round.</em>
</p>
<p align="center">
  <img src="./static/screenshots/custom-mode.png" alt="Custom Mode Form" width="80%">
  <br>
  <em>Custom mode, allowing users to play with their own playlists.</em>
</p>
<p align="center">
  <img src="./static/screenshots/end-game-modal.png" alt="End Game Modal" width="80%">
  <br>
  <em>The end-game screen showing the final score.</em>
</p>

### 🛠️ Tech Stack

This project was built with the following technologies:

**Backend:**
- Python
- Flask
- Flask-Session
- Requests
- thefuzz (for fuzzy string matching)
- cachetools
- python-dotenv

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5

**APIs:**
- Spotify API
- Deezer API

---

### 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

#### Prerequisites

- Python 3.x
- `pip` package manager

#### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/Beyonder230/guess-songs.git](https://github.com/Beyonder230/guess-songs.git)
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd guess-songs
    ```
3.  **Create and activate a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
4.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
5.  **Set up your environment variables:**
    - Create a file named `.env` in the root of the project. This file will hold your secret keys.
    - Add the following three variables to the file:

        ```env
        # 1. Flask Secret Key (for session security)
        # To generate a strong secret key, run this in your terminal:
        # python -c 'import secrets; print(secrets.token_hex(16))'
        FLASK_SECRET_KEY=your_generated_secret_key_here

        # 2. Spotify API Credentials
        # Get these from the Spotify Developer Dashboard.
        SPOTIFY_CLIENT_ID=your_client_id_here
        SPOTIFY_SECRET_ID=your_client_secret_here
        ```

    - **How to get Spotify Credentials:**
        1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
        2.  Log in and click "Create app".
        3.  Give your app a name (e.g., "Guess Songs Clone") and a description.
        4.  Once created, you will see your `Client ID` and you can click "Show client secret" to get the `Client Secret`. Copy and paste them into your `.env` file.

6.  **Run the application:**
    ```sh
    flask run
    ```
7.  Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

### 👤 Author

Developed with ❤️ by **Bruno Vilas Boas Fernandes**.

- **GitHub:** [https://github.com/Beyonder230](https://github.com/Beyonder230)
