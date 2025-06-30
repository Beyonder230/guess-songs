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
 



def get_spotify_tracks_array(url):
    # spotify authentification
    access = get_access()
    if access == None:
        return "auth error"
    
    # http info
    id = get_id_from_url(url, "playlist")
    if id == None:
        return "Could not get id from url"
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
    print(f"Length of tracks_array get from spotify: {len(tracks)}")
    return tracks
    
    
    
def get_random_spotify_track(url):
    tracks = get_spotify_tracks_array(url)
    print(f"return of get_tracks = | {tracks} |")
    if tracks == "Could not get id from url":
        return tracks
    
    # print(f"tracks json: {tracks}")
    if "error" in tracks:
        return "error"
    
    checked_tracks = 0
    
    while checked_tracks < len(tracks):
        random_track = random.choice(tracks["items"])
        title = random_track["track"]["name"]
        artist = random_track["track"]["artists"][0]["name"]
        response = requests.get(f'https://api.deezer.com/search?q=track:"{title}"artist:"{artist}"')
        deezer_track = response.json()
        
        if len(deezer_track["data"]) > 0:
            for item in deezer_track["data"]:
                if item["title"].upper() == title.upper() and item["preview"] != "":
                    return item
        checked_tracks += 1
        
    return "Not eligible track"
    
    
    
def get_random_deezer_track(url):
    if "playlist" in url:
        id = get_id_from_url(url, "playlist")
        url = f"https://api.deezer.com/playlist/{id}"
    elif "album" in url:
        id = get_id_from_url(url, "album")
        url = f"https://api.deezer.com/album/{id}"
    else:
        return "Could not get id from url"
    
    # trying to get the tracks of this playlist
    tracks_url = url + "/tracks"
    # print(f"called URL: {tracks_url}")
    
    # making API request
    tracks_response = requests.get(tracks_url)
    tracks = tracks_response.json()
    final_tracklist = []
    
    # print(f"tracks json: {tracks}")
    if "error" in tracks:
        return "error"
    
    for track in tracks["data"]:
        final_tracklist.append(track)
    
    checked_tracks = 0
    total_tracks = tracks["total"]
    print(f"Length of tracks in the first search of playlist: {len(tracks["data"])}")
    
    while "next" in tracks:
        tracks_response = requests.get(tracks["next"])
        tracks = tracks_response.json()
        
        for track in tracks["data"]:
            final_tracklist.append(track)
        
    print(f"Length of total_tracks used for select a song: {total_tracks}")
    
    while checked_tracks < total_tracks:
        random_track = random.choice(final_tracklist)
        if random_track["preview"] != "":
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
    song = {"title": base_title, "img": base_img, "correct_answer": True, "id": len(options)}
    options.append(song)
    
    while len(options) < 4:
        track = get_random_deezer_track(url)
        img_url = track["album"]["cover_medium"]
        if not check_dict_list(options, "img", img_url):
            title = track["title"]
            song = {"title": title,"img": img_url, "correct_answer": False, "id": len(options)}
            options.append(song)
            
    if len(options) < 4:
        return "error"
    else:
        shuffled_options = random.sample(options, len(options))
        return shuffled_options
    
    
    
 
def get_spotify_options(url, base_song):
    # print the base song used
    print("=" * 200)
    print("BASE SONG:")
    print(base_song)
    print("=" * 200)
    # ======================================
    
    response = get_spotify_tracks_array(url)
    tracks_total = response["total"]
    tracks = response["items"]
    
    print(f"tracks total: {tracks_total}")
    formatted_options = []
    
    base_img = base_song["album"]["cover_medium"]
    base_title = base_song["title"]
    
    song = {"title": base_title, "img": base_img, "correct_answer": True, "id": len(formatted_options)}
    
    
    if base_song["preview"] != "":
        formatted_options.append(song)
    
    checked_tracks = 0
    
    while len(formatted_options) < 4 and checked_tracks <= tracks_total:
        random_track = get_random_spotify_track(url)
        
        img = random_track["album"]["cover_medium"]
        title = random_track["title"]
        song = {"title": title, "img": img, "correct_answer": False, "id": len(formatted_options)}
        
        if random_track["preview"] != "":
            if not check_dict_list(formatted_options, "img", img):
                formatted_options.append(song)
        checked_tracks += 1
    
    if len(formatted_options) < 4:
        return "error"
    else:
        shuffled_options = random.sample(formatted_options, len(formatted_options))
        return shuffled_options
# REFACTOR ==============================================================================================================================================================================
    
    
    
    
def get_tracklist(url):
    if "spotify" in url:
        return get_spotify_tracklist(url)
    elif "deezer" in url:
        return get_deezer_tracklist(url)
    else:
        return None
    
    


def get_spotify_tracklist(url):
    # spotify authentification
    access = get_access()
    if access == None:
        print("Authentification Error")
        return None
    
    # http info
    if "playlist" in url:
        collection = "playlist"
    elif "album" in url:
        collection = "album"
    else:
        print("Error: could not identify playlist or album in url")
        return None
    
    id = get_id_from_url(url, collection)
    if id == None:
        print("Could not get id from url")
        return None
    
    api_url = f"https://api.spotify.com/v1/{collection}s/{id}"
        
    header = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json"
        }
    
    id_counter = 1
    tracks = {"origin": "spotify", "items": []}
    
    while api_url:
        try:
            response = requests.get(api_url, headers=header)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error at spotify API request. {e}")
            return None
        except ValueError:
            print(f"Error at processing data from the spotify API")
            return None
        
        track_page = data.get("tracks", data)
        items = track_page.get('items', [])
        
        for item in items:
            track_data = item.get('track') if 'track' in item else item
            
            if not track_data:
                continue
            
            track = {
                "id": id_counter,
                "artists": [artist["name"] for artist in track_data.get("artists", [])],
                "title": track_data.get("name"),
                "image": track_data.get("album", {}).get("images", [{}])[0].get("url") if "album" in track_data else data.get("images", [{}])[0].get("url")
            }
            tracks["items"].append(track)
            id_counter += 1
            
        api_url = track_page.get("next")
        
    print(f"Length of tracks_array get from spotify: {len(tracks["items"])}")
    print(tracks)
    #print(f"called URL: {url}")

    return tracks




def get_deezer_tracklist(url):
    # http info
    if "playlist" in url:
        collection = "playlist"
    elif "album" in url:
        collection = "album"
    else:
        print("Error: could not identify playlist or album in url")
        return None
    
    id = get_id_from_url(url, collection)
    if id == None:
        print("Could not get id from url")
        return None
    
    api_url = f"https://api.deezer.com/{collection}/{id}/tracks"
    tracks = {"origin": "deezer", "items": []}
    id_counter = 1
    
    while api_url:
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error at deezer API request. {e}")
            return None
        except ValueError:
            print(f"Error at processing data from the deezer API")
            return None
        
        for track_data in data.get("data"):
            if not track_data:
                continue
            
            preview_url = track_data.get("preview")
            if not preview_url:
                continue

            artist = track_data.get("artist")
            if artist:
                artist_name = artist.get("name")
            else:
                artist_name = "unknown artist"
            
            track = {
                "id": id_counter,
                "artists": [artist_name],
                "title": track_data.get("title"),
                "image": track_data.get("album", {}).get("cover_medium"),
                "preview": preview_url
            }
            tracks["items"].append(track)
            id_counter += 1
            
        api_url = data.get("next")
        
    print(f"Length of tracks_array get from deezer: {len(tracks["items"])}")
    print(tracks)
    #print(f"called URL: {url}")

    return tracks