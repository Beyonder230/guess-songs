from datetime import timedelta
import requests
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect, url_for
from helpers import get_access, get_random_track, get_options

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
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

@app.route('/singleplayer', methods=["GET", "POST"])
def singleplayer():
    if request.method == "POST":
        data = request.get_json()
        title = data.get("current_title")
        new_score = data.get("current_score")
        
    if "singleplayer_score" not in session:
        session.permanent = True
        session["singleplayer_score"] = 0
        
    token = get_access()
    if token == None:
        return "auth error"
    
    # default playlist for this gamemode
    playlist_url = "https://www.deezer.com/br/playlist/4461060364"
    
    # test_access(token)
    track = get_random_track(playlist_url, token)
        
    print(f"return of get_random_track(): {track}")
    if track == "error":
        return redirect("/error")
    
    # get info about the answer options
    options = get_options(playlist_url, track)
    print(f"return of get_options(): {options}")
    if options == "error":
        return redirect("/error")
    
    if request.method == "POST":
        return redirect(url_for("singleplayer", score = new_score))
    else:
        return render_template("game.html", bigger_score = session["singleplayer_score"], song = track, options = options, score = 0)

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/attributions")
def attributions():
    return render_template("attributions.html")

if __name__ == "__main__":
    app.run(debug=True)