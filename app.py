import random
import urllib.parse
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect, flash, jsonify, make_response, url_for
from helpers import get_tracklist, get_audio_as_base64, get_preview_with_id, get_id_from_url, get_playlist_in_cache
from flask_session import Session
from whitenoise import WhiteNoise
import threading

load_dotenv()

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.environ.get("FLASK_SECRET_KEY")


Session(app)

app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/")



TASK_STATUS = {}

def get_max_score(gamemode, current_score, cookies):
    cookie_name = f"{gamemode}_score"
    old_max_score = int(cookies.get(cookie_name, 0))
    
    if current_score > old_max_score:
        return current_score
    else:
        return old_max_score
    
    
    
    
@app.route('/')
def index():
    return render_template("index.html")




@app.route("/howthegameworks")
def howthegameworks():
    return render_template("rules.html")




@app.route("/gamemodes")
def gamemodes():
    return render_template("gamemodes.html")




@app.route("/error")
def error():
    return render_template("error.html")




@app.route("/attributions")
def attributions():
    return render_template("attributions.html")




@app.route("/get_game_data")
def get_game_data():
    tracklist_data = session.get("tracklist", {})
    playable_tracks = tracklist_data.get("playable_tracks", [])
    options_tracks = tracklist_data.get("options_tracks", [])
    
    if not playable_tracks:
        return make_response(jsonify({"win": True}))

    chose_track = random.choice(playable_tracks)
    
    preview_url = chose_track.get("preview")
    #print(f"Fetching audio for '{chose_track.get('title')}'...")
    audio_data_url = get_audio_as_base64(preview_url)
    
    if audio_data_url:
        chose_track["preview"] = audio_data_url
    else:
        title = chose_track.get("title")
        artist = chose_track.get("artist")
        chose_track["preview"] = get_audio_as_base64(get_preview_with_id(title, artist))
    
    correct_option = next((opt for opt in options_tracks if opt.get('id') == chose_track.get('id')), None)
    if correct_option is None:
        return make_response(jsonify({"error": "Data inconsistency."})), 500

    selected_options = [correct_option]
    
    wrong_options_pool = [opt for opt in options_tracks if opt.get('id') != chose_track.get('id')]
    num_to_sample = min(len(wrong_options_pool), 3)
    wrong_options = random.sample(wrong_options_pool, k=num_to_sample)
    
    selected_options.extend(wrong_options)
    
    random.shuffle(selected_options)
    
    response = make_response(jsonify({
        "win": False,
        "song": chose_track,
        "options": selected_options,
        "playable_tracks_size": len(playable_tracks)
    }))
    
    return response




@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.get_json()
    selected_id = data.get("selected_id")
    correct_id = data.get("correct_id")
    gamemode = data.get("gamemode")
    
    if not gamemode:
        return jsonify({"status": "error", "message": "Gamemode not provided."}), 400
    if not selected_id:
        return jsonify({"status": "error", "message": "SongID from selected object not provided."}), 400
    if not correct_id:
        return jsonify({"status": "error", "message": "Correct song ID not provided."}), 400
    
    tracklist_data = session.get("tracklist", {})
    if tracklist_data:
        playable_tracks = tracklist_data.get("playable_tracks", [])
        
        playable_tracks = [track for track in playable_tracks if str(track.get("id")) != str(correct_id)]
        session["tracklist"]["playable_tracks"] = playable_tracks
    
    if str(correct_id) == str(selected_id):
        session["score"] = session.get("score", 0) + 1
        session.modified = True
        
        max_score = get_max_score(gamemode, session["score"], request.cookies)
        
        response_data = {"result": "correct", "score": session["score"], "correct_song_id": correct_id, "max_score": max_score}
        response = make_response(jsonify(response_data))
        response.set_cookie(f"{gamemode}_score", str(max_score),  max_age=31536000)
    else:
        max_score = int(request.cookies.get(f"{gamemode}_score", 0))
        response = jsonify({"result": "wrong", "score": session.get("score", 0), "correct_song_id": correct_id, "max_score": max_score})
        
    session.modified = True
    return response
        
        
        
    
def start_game(url, gamemode, time):
    if "playlist" in url:
        collection = "playlist"
    elif "album" in url:
        collection = "album"
    else:
        return None
    
    id = get_id_from_url(url, collection)  
    
    if TASK_STATUS.get(id) == "processing":
        return jsonify({"message": "This playlist is beeing processed", "task_id": id})  
    
    thread = threading.Thread(target=process_playlist_thread, args=(url, id))
    thread.start()
    
    max_score = int(request.cookies.get(f"{gamemode}_score", 0))
    session["max_score"] = max_score
    session["time"] = time
    session["gamemode"] = gamemode
    session["original_url"] = url
    session.modified = True
    
    return jsonify({"message": "This playlist is beeing processed", "task_id": id})  


    
@app.route("/custom", methods=["POST"])
def custom():    
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request."}), 400

    url = data.get("url")
    time_str = data.get("time")

    if not url or not time_str:
        return jsonify({"status": "error", "message": "All fields must be filled."}), 400
    
    try:
        time = int(time_str)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "The time must be a whole number (e.g., 30)."}), 400

    url = urllib.parse.unquote_plus(url)
    return start_game(url, "custom", time)




@app.route("/singleplayer", methods=["GET", "POST"])
def singleplayer():
    # default playlist for this gamemode
    playlist_url = "https://www.deezer.com/br/playlist/3155776842"
    gamemode = "singleplayer"
    time = 15
    
    tracklist = get_tracklist(playlist_url)
    if not tracklist or len(tracklist.get("playable_tracks", [])) < 5:
        flash("This playlist is a bit short! Please choose a playlist or album with at least 5 playable tracks.")
        return redirect(url_for("gamemodes"))

    session["tracklist"] = tracklist
    session["score"] = 0
    session["gamemode"] = gamemode
    session["time"] = time
    session.modified = True

    return redirect(url_for("game_page")) 




def process_playlist_thread(url, id):
    TASK_STATUS[id] = "processing"
    
    result = get_tracklist(url)
    
    if result and result.get("playable_tracks"):
        TASK_STATUS[id] = "completed"
    else:
        TASK_STATUS[id] = "error"




@app.route("/task_status/<string:task_id>")
def task_status(task_id):
    status = TASK_STATUS.get(task_id, "not_found")
    if status == "completed":
        tracklist = get_playlist_in_cache(task_id)
        
        if not tracklist:
            flash("Couldn't load the playlist. Please check if the link is correct and make sure the playlist is public.")
            return redirect("/gamemodes")
        elif len(tracklist.get("playable_tracks", [])) < 5:
            flash("This playlist is a bit short! Please choose a playlist or album with at least 5 playable tracks.")
            return redirect("/gamemodes")

        total_tracks = tracklist.get("total_tracks", 0)
        loaded_tracks = len(tracklist.get("options_tracks", []))
        
        if total_tracks > loaded_tracks and loaded_tracks > 0:
            flash(f"Warning: This playlist is too big! The game was loaded with the first {loaded_tracks} tracks.")

        session["tracklist"] = tracklist
        session["score"] = 0
        session.modified = True

        return jsonify({
            "status": "completed",
            "redirect_url": url_for("game_page")
        })
    else:
        return jsonify({"status": status})




@app.route("/game")
def game_page():
    gamemode = session.get("gamemode", "custom")
    time = session.get("time", 15)
    max_score = int(request.cookies.get(f"{gamemode}_score", 0))
    url = session.get("original_url", {})
    
    return render_template("game.html", bigger_score=max_score, gamemode=gamemode, time=time, url=url)