from datetime import timedelta
import urllib.parse
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect, flash, jsonify, make_response
from helpers import get_tracklist
from flask_session import Session

load_dotenv()

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=99)

Session(app)




@app.route('/')
def index():
    return render_template("index.html")




@app.route("/howthegameworks")
def howthegameworks():
    return render_template("rules.html")




@app.route("/gamemodes")
def play():
    return render_template("gamemodes.html")




@app.route("/error")
def error():
    return render_template("error.html")




@app.route("/attributions")
def attributions():
    return render_template("attributions.html")




@app.route("/get_game_data", methods=["POST"])
def get_game_data():
    return #TODO




@app.route("/score_update", methods=["POST"])
def score_update():
    data = request.get_json()
    gamemode = data.get("gamemode")
    new_score = data.get("new_score")
    
    if not gamemode or new_score is None:
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400
    
    mode_score = f"{gamemode}_score"
    old_score = int(request.cookies.get(mode_score, 0))
    
    response = make_response(jsonify({
        "status": "success", 
        "mensagem": "Score updated."
    }))
    
    if new_score > old_score:
        response.set_cookie(mode_score, str(new_score), max_age=31536000)
        
    return response
        
        
        
        
@app.route("/custom", methods=["POST"])
def custom():    
    time = request.form.get("time")
    url = request.form.get("url")
    
    if not url or not time:
        flash("Validation error: all fields must be filled")
        return redirect("/gamemodes")
    
    try:
        time = int(time)
    except (ValueError, TypeError):
        flash("Validation error: time variable is not a integer number")
        return redirect("/gamemodes")

    url = urllib.parse.unquote_plus(url)
    tracklist = get_tracklist(url)
 
    if tracklist is None:
        flash("Error: Unable to read url id, check your input.")
        return redirect("/gamemodes")
    
    session["tracklist"] = tracklist
    max_score = session.get("custom_score", 0)
    
    return render_template("game.html", bigger_score = max_score, gamemode = "custom", url=url, time=time)




@app.route("/singleplayer")
def singleplayer():
    time = 15
    # default playlist for this gamemode
    playlist_url = "https://www.deezer.com/br/playlist/4461060364"
    tracklist = get_tracklist(playlist_url)
        
    if tracklist is None:
        flash("Error: Unable to read url id, check your input.")
        return redirect("/gamemodes")

    session["tracklist"] = tracklist
    max_score = session.get("singleplayer_score", 0)
    
    return render_template("game.html", bigger_score = max_score, gamemode = "singleplayer", time=time)




if __name__ == "__main__":
    app.run(debug=True)