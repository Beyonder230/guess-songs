from datetime import timedelta
import urllib.parse
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect, url_for
from helpers import get_access, get_deezer_options, get_spotify_options, get_random_deezer_track, get_random_spotify_track

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
    if "best_singleplayer_score" not in session:
        session.permanent = True
        session["best_singleplayer_score"] = 0
    else:
        if session["singleplayer_score"] > session["best_singleplayer_score"]:
            session["best_singleplayer_score"] = session["singleplayer_score"]
     
    # default playlist for this gamemode
    playlist_url = "https://www.deezer.com/br/playlist/4461060364"
    track = get_random_deezer_track(playlist_url)
        
    # print(f"return of get_random_track(): {track}")
    if track == "error":
        return redirect("/error")
    
    # get info about the answer options
    options = get_deezer_options(playlist_url, track)
    # print(f"return of get_options(): {options}")
    if options == "error":
        return redirect("/error")
    
    time = 15

    return render_template("game.html", bigger_score = session["best_singleplayer_score"], song = track, options = options, score = session["singleplayer_score"], gamemode = "singleplayer", time=time)




@app.route("/error")
def error():
    return render_template("error.html")




@app.route("/attributions")
def attributions():
    return render_template("attributions.html")




@app.route("/score_update/custom/<path:url>/<int:time>")
def score_custom(url, time):
    mode_score = "custom_score"
    
    if mode_score not in session:
        session[mode_score] = 0
    
    session[mode_score] += 1
    

    url = urllib.parse.quote_plus(url, safe='')
        
    return redirect(url_for("custom", url=url, time=time))
    
    
    
    
@app.route("/score_update/<string:gamemode>")
def score_update(gamemode):
    mode_score = f"{gamemode}_score"
    
    if mode_score not in session:
        session[mode_score] = 0
    
    session[mode_score] += 1
    
    if gamemode == "custom":
        url = urllib.parse.quote_plus(url, safe='')
            
        return redirect(url_for(gamemode, url=url))
    else:
        return redirect(url_for(gamemode))




@app.route("/score_reset/<string:gamemode>", methods=["GET", "POST"])
def score_reset(gamemode):
    mode_score = f"{gamemode}_score"
    
    session[mode_score] = 0
    
    if mode_score not in session:
        session[mode_score] = 0
        
    if request.method == "GET":
        return redirect("/gamemodes")
    elif request.method == "POST":
        if gamemode == "custom":
            time = request.form.get("time")
            try:
                time = int(time)
            except:
                print("Validation error: time variable is not a integer")
                return redirect("/error")
            
            url = request.form.get("url")
            url = urllib.parse.quote_plus(url, safe='')
            
            print(f"url: {url}")
            return redirect(url_for(gamemode, url=url, time=time))
        else:
            return redirect(url_for(gamemode))
        
        
        
        
@app.route("/custom/<string:url>/<int:time>", methods=["GET", "POST"])
def custom(url, time):    
    url = urllib.parse.unquote_plus(url)
    
    # session score
    if "best_custom_score" not in session:
        session.permanent = True
        session["best_custom_score"] = 0
    if "custom_score" not in session:
        session["custom_score"] = 0

    if session["custom_score"] > session["best_custom_score"]:
        session["best_custom_score"] = session["custom_score"]
    
    # selecting a random track
    if "spotify" in url:
        track = get_random_spotify_track(url)
    elif "deezer" in url:
        track = get_random_deezer_track(url)
    else:
        print(f"error in selecting a random track / url: {url}")
        return redirect("/error")
        
    # print(f"return of get_random_track(): {track}")
    if track == "error":
        return redirect("/error")
    
    # get info about the answer options
    if "spotify" in url:
        options = get_spotify_options(url, track)
    elif "deezer" in url:
        options = get_deezer_options(url, track)
    else:
        print(f"error in getting options / url: {url}")
        return redirect("/error")

    # print(f"return of get_options(): {options}")
    if options == "error":
        return redirect("/error")

    return render_template("game.html", bigger_score = session["best_custom_score"], song = track, options = options, score = session["custom_score"], gamemode = "custom", url=url, time=time)

if __name__ == "__main__":
    app.run(debug=True)