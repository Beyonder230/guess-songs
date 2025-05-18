from datetime import timedelta
import requests
from flask import Flask, render_template, session, request, redirect
from helpers import get_access, get_random_track, get_id_from_url, test_access

app = Flask(__name__)
app.secret_key = ***REMOVED***
app.permanent_session_lifetime = timedelta(days=99)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/howthegameworks')
def howthegameworks():
    return render_template("rules.html")

@app.route('/gamemodes')
def play():
    return render_template("gamemodes.html")

@app.route('/singleplayer', methods=["POST"])
def singleplayer():
    if "singleplayer_score" not in session:
        session.permanent = True
        session["singleplayer_score"] = 0
    token = get_access()
    if token == None:
        return "auth error"
    
    playlist_url = "https://open.spotify.com/playlist/09tJur2DIOM35bqoVXDjgw?si=df9b3362229f47f1"
    playlist_id = get_id_from_url(playlist_url, "playlist")
    if playlist_id == None:
        return "wrong playlist"
    
    # test_access(token)
    track = get_random_track(playlist_id, token)
    print(f"return of get_random_track(): {track}")
    
    return render_template("singleplayer.html", bigger_score = session["singleplayer_score"])


if __name__ == "__main__":
    app.run(debug=True)