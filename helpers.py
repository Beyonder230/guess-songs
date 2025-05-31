import requests
import random
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def get_access():
    url = "https://accounts.spotify.com/api/token"
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_SECRET_ID")
    
    credentials = f"{client_id}:{client_secret}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    header = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"}
    
    body = "grant_type=client_credentials"
    
    response = requests.post(url, headers=header, data=body)
    
    # print(f"acess_token variable: {response}")
    
    response_data = response.json()
    # print(f"acess_token json: {response_data}")
    
    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        print("Token generating error", response_data)
        return None




''' separate in two functions (spotify and deezer get random track)
def get_random_track(playlist_url, access):
    # http info
    if "spotify" in playlist_url:
        playlist_id = get_id_from_url(playlist_url, "playlist")
        if playlist_id == None:
            return "Wrong playlist"
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    elif "deezer" in playlist_url:
        if "playlist" in playlist_url:
            playlist_id = get_id_from_url(playlist_url, "playlist")
        elif "album" in playlist_url:
            playlist_id = get_id_from_url(playlist_url, "album")
        if playlist_id == None:
            return "Wrong playlist"
        url = f"https://api.deezer.com/playlist/{playlist_id}"
        
    header = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json"
        }
    
    # trying to get the tracks of this playlist
    tracks_url = url + "/tracks"
    print(f"called URL: {tracks_url}")
    
    if "spotify" in playlist_url:
        tracks_response = requests.get(tracks_url, headers=header)
    if "deezer" in playlist_url:
         tracks_response = requests.get(tracks_url)
    tracks = tracks_response.json()
    
    # print(f"tracks json: {tracks}")
    
    if "error" in tracks:
        return "error"
    
    checked_tracks = 0
    if "spotify" in playlist_url:
        total_tracks = len(tracks["items"])
        while checked_tracks < total_tracks:
            random_track = random.choice(tracks["items"])
            if random_track["track"]["preview_url"] != None:
                return random_track
            checked_tracks += 1
    elif "deezer" in playlist_url:
        total_tracks = len(tracks["data"])
        while checked_tracks < total_tracks:
            random_track = random.choice(tracks["data"])
            if random_track["preview"] != None:
                return random_track
            checked_tracks += 1
 
    return "There's no elligible track in the playlist"
    # currently this is an simple version of the function bc its only consider the first 50 tracks (ok for the top 50 global default playlist)
'''
   
   
   
   
def get_id_from_url(url, type):
    type = type + "/"
    if type in url:
        print(f"playlist_id = {url.split(type)[1].split("?")[0]}")
        return url.split(type)[1].split("?")[0]
    return None # error return




'''
def get_options(playlist_url, base_song):
    print("=" * 200)
    print("BASE SONG:")
    print(base_song)
    print("=" * 200)
    if "spotify" in playlist_url:
        base_img = base_song["track"]["album"]["images"]["url"]
        base_title = base_song["track"]["name"]
    elif "deezer" in playlist_url:
        base_img = base_song["album"]["cover_medium"]
        base_title = base_song["title"]
        
    options = []
    song = {"title": base_title, "img": base_img, "correct_answer": True}
    options.append(song)
    
    if "spotify" in playlist_url:
        token = get_access()
        if token == None:
            return "auth error"
    
    while len(options) < 4:
        if "spotify" in playlist_url:
            track = get_random_spotify_track(playlist_url, token)
            img_url = track["track"]["album"]["images"]["url"]
            if not check_dict_list(options, "img", img_url):
                title = track["track"]["name"]
                song = {"title": title,"img": img_url, "correct_answer": False}
                options.append(song)
        elif "deezer" in playlist_url:
            track = get_random_deezer_track(playlist_url)
            img_url = track["album"]["cover_medium"]
            if not check_dict_list(options, "img", img_url):
                title = track["title"]
                song = {"title": title,"img": img_url, "correct_answer": False}
                options.append(song)
            
    if len(options) < 4:
        return "error"
    else:
        shuffled_options = random.sample(options, len(options))
        return shuffled_options
'''




def check_dict_list(list, key, element):
    for dict in list:
        if key in dict and element in dict[key]:
            return True
    return False
 



def get_random_spotify_track(url, access):
    # http info
    id = get_id_from_url(url, "playlist")
    if id == None:
        return "Wrong playlist"
    url = f"https://api.spotify.com/v1/playlists/{id}"
        
    header = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json"
        }
    
    # trying to get the tracks of this playlist
    tracks_url = url + "/tracks"
    print(f"called URL: {tracks_url}")
    
    tracks_response = requests.get(tracks_url, headers=header)
    tracks = tracks_response.json()
    
    # print(f"tracks json: {tracks}")
    if "error" in tracks:
        return "error"
    
    checked_tracks = 0
    total_tracks = len(tracks["items"])
    while checked_tracks < total_tracks:
        random_track = random.choice(tracks["items"])
        if random_track["track"]["preview_url"] != None:
            return random_track
        checked_tracks += 1
 
    return "There's no elligible track in the playlist"
    # currently this is an simple version of the function bc its only consider the first 50 tracks (ok for the top 50 global default playlist)
    
    
    
    
def get_random_deezer_track(url):
    if "playlist" in url:
        id = get_id_from_url(url, "playlist")
        url = f"https://api.deezer.com/playlist/{id}"
    elif "album" in url:
        id = get_id_from_url(url, "album")
        url = f"https://api.deezer.com/album/{id}"
        
    if id == None:
        return "Wrong playlist"
    
    # trying to get the tracks of this playlist
    tracks_url = url + "/tracks"
    print(f"called URL: {tracks_url}")
    
    # making API request
    tracks_response = requests.get(tracks_url)
    tracks = tracks_response.json()
    
    # print(f"tracks json: {tracks}")
    
    if "error" in tracks:
        return "error"
    
    checked_tracks = 0
    total_tracks = len(tracks["data"])
    while checked_tracks < total_tracks:
        random_track = random.choice(tracks["data"])
        if random_track["preview"] != None:
            return random_track
        checked_tracks += 1
 
    return "There's no elligible track in the playlist"
    # currently this is an simple version of the function bc its only consider the first 50 tracks (ok for the top 50 global default playlist)
    



def get_deezer_options(url, base_song):
    # print the base song used
    print("=" * 200)
    print("BASE SONG:")
    print(base_song)
    print("=" * 200)
    # ======================================
    
    if "playlist" in url:
        base_img = base_song["album"]["cover_medium"]
        base_title = base_song["title"]
    else:
        return "error"
        
    options = []
    song = {"title": base_title, "img": base_img, "correct_answer": True}
    options.append(song)
    
    while len(options) < 4:
        track = get_random_deezer_track(url)
        img_url = track["album"]["cover_medium"]
        if not check_dict_list(options, "img", img_url):
            title = track["title"]
            song = {"title": title,"img": img_url, "correct_answer": False}
            options.append(song)
            
    if len(options) < 4:
        return "error"
    else:
        shuffled_options = random.sample(options, len(options))
        return shuffled_options
    
    
    
 
# TODO   
def get_spotify_options(url, base_song):
    # print the base song used
    print("=" * 200)
    print("BASE SONG:")
    print(base_song)
    print("=" * 200)
    # ======================================
    
    if "playlist" in url:
        base_img = base_song["album"]["cover_medium"]
        base_title = base_song["title"]
    elif "album" in url:
        base_img = base_song["cover_medium"]
        base_title = base_song["title"]
        
    options = []
    song = {"title": base_title, "img": base_img, "correct_answer": True}
    options.append(song)
    
    while len(options) < 4:
        if "deezer" in url:
            track = get_random_deezer_track(url)
            img_url = track["album"]["cover_medium"]
            if not check_dict_list(options, "img", img_url):
                title = track["title"]
                song = {"title": title,"img": img_url, "correct_answer": False}
                options.append(song)
            
    if len(options) < 4:
        return "error"
    else:
        shuffled_options = random.sample(options, len(options))
        return shuffled_options