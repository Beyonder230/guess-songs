import requests
import base64
import os
from dotenv import load_dotenv
import urllib
from thefuzz import fuzz
import re
from concurrent.futures import ThreadPoolExecutor
import time
from cachetools import TTLCache
import threading
import random


load_dotenv()
deezer_id_cache = TTLCache(maxsize=2000, ttl=864000)
spotify_token_cache = TTLCache(maxsize=1, ttl=3500)
playlist_cache = TTLCache(maxsize=20, ttl=600)

LOCK = threading.Lock()

def get_access():
    if "access_token" in spotify_token_cache:
        return spotify_token_cache["access_token"]
    
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
        spotify_token_cache["access_token"] = response_data["access_token"]
        return response_data["access_token"]
    else:
        #print("Token generating error", response_data)
        return None



   
def get_id_from_url(url, type):
    type = type + "/"
    if type in url:
        #print(f"playlist_id = {url.split(type)[1].split("?")[0]}")
        return url.split(type)[1].split("?")[0]
    return None # error return
# REFACTOR ==============================================================================================================================================================================
    
    
    
    
def get_tracklist(url):
    if "playlist" in url:
        collection = "playlist"
    elif "album" in url:
        collection = "album"
    else:
        #print("Error: could not identify playlist or album in url")
        return None
    
    id = get_id_from_url(url, collection)
    if not id:
        #print("Could not get id from url")
        return None
    
    if cache_playlist_validation(id):
        return playlist_cache[id]
        
    with LOCK:
        if cache_playlist_validation(id):
            return playlist_cache[id]
        
        if "spotify" in url:
            return get_spotify_tracklist(id, collection)
        elif "deezer" in url:
            return get_deezer_tracklist(id, collection)




def get_spotify_tracklist(id, collection):
    # spotify authentification
    access = get_access()
    if access == None:
        #print("Authentification Error")
        return None
    
    BASE_URL = "https://api.spotify.com/v1"
        
    header = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json"
        }
    
    api_url = None
    album_cover_url = None
    
    needed_fields = "items(track(id,name,preview_url,artists(name),album(images))),next,total"
    encoded_fields = urllib.parse.quote(needed_fields)

    # IF ALBUM THIS IS THE FIRST CALL TO GET ALBUM COVER
    # PREPARE THE NEXT URL TO CALL
    try:
        if collection == "album":
            album_response = requests.get(f"{BASE_URL}/albums/{id}", headers=header)
            album_response.raise_for_status()
            album_data = album_response.json()
            
            album_images = album_data.get("images", [])
            album_cover_url = album_images[0].get("url") if album_images else None
            
            api_url = f"{BASE_URL}/albums/{id}/tracks?limit=50"
        elif collection == "playlist":
            api_url = f"{BASE_URL}/playlists/{id}/tracks?limit=100&fields={encoded_fields}"
    except requests.exceptions.RequestException as e:
        #print(f"Error at first spotify API call: {e}")
        return None
    
    playable_tracks, options_tracks = [], []
    id_counter, total_tracks = 1, 0
    first_call = True
    found_tracks = set()
    
    while api_url:
        try:
            response = requests.get(api_url, headers=header)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            #print(f"Error at spotify API request. {e}")
            return None
        except ValueError:
            #print(f"Error at processing data from the spotify API")
            return None
        
        if first_call:
            total_tracks = data.get("total", 0)
            first_call = False
        
        for item in data.get("items", []):
            track_data = item.get("track") if "track" in item else item
            
            if not track_data or not track_data.get("name"):
                continue
            
            title = track_data.get("name")
            
            artists_list = track_data.get("artists", [])
            artist = artists_list[0].get("name") if len(artists_list) > 0 else None
            
            if (title, artist) in found_tracks:
                continue
            
            image_url = album_cover_url if collection == "album" else None
            if not image_url:
                track_album_images  = track_data.get("album", {}).get("images", []) 
                image_url = track_album_images [0].get("url") if track_album_images else "/static/default_cover.png"
            
            options_track = {
                "id": id_counter,
                "title": track_data.get("name"),
                "image": image_url
            }
            options_tracks.append(options_track)
            
            if track_data.get("preview_url"):
                preview = track_data.get("preview_url")
            else:
                preview = get_preview_from_deezer(title, artist)
            
            playable_track = {
                "id": id_counter,
                "preview": preview,
                "artist": artist,
                "title": title
            }
            playable_tracks.append(playable_track)
            
            found_tracks.add((title, artist))
            id_counter += 1
          
        if len(playable_tracks) >= 150:
            break
        
        api_url = data.get("next")
        #print(f"next field = {api_url}")
        
    tracks_with_preview = [track for track in playable_tracks if track["preview"]]
    tracks_without_preview = [track for track in playable_tracks if not track["preview"]]
    found_previews = {}
    
    if tracks_without_preview:
        batch_size = 50
        max_workers_per_batch = 10
        
        for i in range(0, len(tracks_without_preview), batch_size):
            batch_of_tracks = tracks_without_preview[i:i + batch_size]
            
            with ThreadPoolExecutor(max_workers=max_workers_per_batch) as executor:
                args = [(track.get("title"), track.get("artist") if track.get("artist") else None) for track in batch_of_tracks]
                results = list(executor.map(lambda p: get_preview_from_deezer(*p), args))
            
                for j, track in enumerate(batch_of_tracks):
                    if results[j]:
                        found_previews[track.get("id")] = results[j]
                    
            time.sleep(1)
        
    for track in tracks_without_preview:
        if track.get("id") in found_previews:
            track["preview"] = found_previews[track.get("id")]
            tracks_with_preview.append(track)
        
    #print(f"Length of total tracks get from spotify: {len(options_tracks)}")
    #print(f"Length of playable tracks get from spotify: {len(tracks_with_preview)}")
    #print(f"called URL: {url}")
    
    playlist_cache[id] = {"playable_tracks": tracks_with_preview, "options_tracks": options_tracks, "total_tracks": total_tracks}
    return {"playable_tracks": tracks_with_preview, "options_tracks": options_tracks, "total_tracks": total_tracks}




def get_deezer_tracklist(id, collection):
    api_url = f"https://api.deezer.com/{collection}/{id}"
    playable_tracks = []
    options_tracks = []
    id_counter = 1
    first_call = True
    
    while api_url:
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            #print(f"Error at deezer API request. {e}")
            return None
        except ValueError:
            #print(f"Error at processing data from the deezer API")
            return None
        
        if first_call == True:
            total_tracks = data.get("nb_tracks")
            if collection == "album":
                album_cover = data.get("cover_medium", "/static/default_cover.png")
            
        track_source = data.get("tracks", data)
        items_list = track_source.get("data", [])
            
        for track_data in items_list:
            if not track_data:
                continue
            
            title = track_data.get("title")
            artist = track_data.get("artist", {}).get("name")
            
            options_track = {
                "id": id_counter,
                "title": title,
                "image": track_data.get("album", {}).get("cover_medium", "/static/default_cover.png") if collection == "playlist" else album_cover
            }
            options_tracks.append(options_track)
            
            preview_url = track_data.get("preview")
            if preview_url:
                playable_track = {
                    "id": id_counter,
                    "preview": preview_url,
                    "artist": artist,
                    "title": title
                }
                playable_tracks.append(playable_track)
            
            cache_key = (title, artist)
            if cache_key not in deezer_id_cache:
                deezer_id_cache[cache_key] = track_data.get("id")
            
            id_counter += 1
        
        api_url = data.get("next")
        first_call = False
        
    #print(f"Length of total tracks get from deezer: {len(options_tracks)}")
    #print(f"Length of playable tracks get from deezer: {len(playable_tracks)}")
    #print(f"called URL: {url}")

    return {"playable_tracks": playable_tracks, "options_tracks": options_tracks, "total_tracks": total_tracks}




def _normalize_title(title):
    if not title:
        return None
    
    normalized = title.lower()
    normalized = normalized.replace('&', "and")
    normalized = re.sub(r'[\(\)\[\]]', '', normalized)
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized
    
    
    
    
def _clean_search_title(title):
    title = re.sub(r'\s*\(\s*', '(', title)
    title = re.sub(r'\s*\)\s*', ')', title)
    title = re.sub(r'\([^)]*\)', '', title)
    
    title = re.sub(r'\s*\(\s*', '[', title)
    title = re.sub(r'\s*\)\s*', ']', title)
    title = re.sub(r'\[[^)]*\]', '', title)
    
    title = re.sub(r'\s*-\s*', '-', title)
    title = re.sub(r'-.*', '', title)
    final_title = title.strip()
    
    return final_title
    
    
    
    
    
def get_preview_from_deezer(title, primary_artist):
    if not primary_artist or not title:
        #print(f"Not found artist '{primary_artist}' or title '{title}'")
        return None
    
    cache_key = (title, primary_artist)
    if cache_key in deezer_id_cache:
        return get_preview_with_id(title, primary_artist)
    deezer_id = None
        
    normalized_spotify_title = _normalize_title(title)
    clean_spotify_title = _clean_search_title(title)
    
    safe_title = urllib.parse.quote_plus(clean_spotify_title)
    safe_artist = urllib.parse.quote_plus(primary_artist)
    
    api_url = f'https://api.deezer.com/search?q=track:"{safe_title}"artist:"{safe_artist}"'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("data", [])
        if not search_results:
            #print(f"Spotify music '{title}' for artist {primary_artist} could not find a deezer version")
            result = None

        best_match = None
        highest_score = -1
        
        best_partial_match = None
        highest_partial_score = -1
        
        best_clean_match = None
        highest_clean_score = -1
        
        for item in search_results:
            deezer_title = item.get("title", "")
            normalized_deezer_title = _normalize_title(deezer_title)
            clean_deezer_title = _clean_search_title(deezer_title)
            
            score = fuzz.ratio(normalized_spotify_title, normalized_deezer_title)
            partial_score = fuzz.partial_ratio(normalized_spotify_title, normalized_deezer_title)
            clean_score = fuzz.partial_ratio(_normalize_title(clean_deezer_title), _normalize_title(clean_spotify_title))
            
            if score > highest_score:
                highest_score = score
                best_match = item
                
            if partial_score > highest_partial_score:
                highest_partial_score = partial_score
                best_partial_match = item
                
            if clean_score > highest_clean_score:
                highest_clean_score = clean_score
                best_clean_match = item
                
        CONFIDENCE_THRESHOLD = 85
        if highest_score >= CONFIDENCE_THRESHOLD:
            #print(f"    -> Best match found ({highest_score}%). '{best_match.get("title")}'")
            deezer_id = best_match.get("id")
            result = best_match.get("preview")
        elif highest_partial_score >= CONFIDENCE_THRESHOLD:
            #print(f"    -> Best match found *partial match* ({highest_partial_score}%). '{best_partial_match.get("title")}'")
            deezer_id = best_partial_match.get("id")
            result = best_partial_match.get("preview")
        elif highest_clean_score >= CONFIDENCE_THRESHOLD:
            #print(f"    -> Best match found *cleaned match* ({highest_clean_score}%). '{best_clean_match.get("title")}'")
            deezer_id = best_clean_match.get("id")
            result = best_clean_match.get("preview")
        else:
            #if best_match:
                #print(f"    -> Best match found ({highest_score}%), but under the confidence threshold. '{best_match.get("title")}'")
            #else:
                #print(f"Title of spotify music not found in deezer: '{title}' for artist: {primary_artist}")
            result = None
    
    except requests.exceptions.RequestException as e:
        #print(f"Request error: could not search for {title} in deezer. {e}")
        result = None
    except ValueError:
        #print(f"Data error: Invalid answer from deezer API searching from {title}")
        return None
    
    deezer_id_cache[cache_key] = deezer_id
    return result




def get_audio_as_base64(url):
    """
    Fetches an audio file from a URL and encodes it into a Base64 Data URL.
    """
    if not url:
        return None
    try:
        # Fetch the audio file content
        response = requests.get(url, timeout=10) # Added a timeout for safety
        response.raise_for_status()
        
        # Get the correct content type (e.g., 'audio/mpeg')
        content_type = response.headers['Content-Type']
        # Encode the binary content to a Base64 string
        encoded_audio = base64.b64encode(response.content).decode('utf-8')
        
        return f"data:{content_type};base64,{encoded_audio}"
        
    except requests.exceptions.RequestException as e:
        #print(f"Error fetching audio for proxy: {e}")
        return None
    
    


def cache_playlist_validation(id):
    if not id:
        return False
    
    if id not in playlist_cache:
        return False
    
    cached_data = playlist_cache[id]
    playable_tracks = cached_data.get("playable_tracks", [])
    
    if playable_tracks:
        sample_track = random.choice(playable_tracks)
        sample_url = sample_track.get("preview")
        
        if get_audio_as_base64(sample_url):
            return True
        else:
            return False
    else:
        return False
    



def get_preview_with_id(title, artist):
    if (title, artist) in deezer_id_cache:
        id = deezer_id_cache[(title, artist)]
    else:
        return None

    if not id:
        #print(f"id '{id}' not in cache.")
        return None
    
    api_url = f'https://api.deezer.com/track/{id}'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        result = data.get("preview")
    except requests.exceptions.RequestException as e:
        #print(f"Request error: could not search for id '{id}' in deezer. {e}")
        result = None
    except ValueError:
        #print(f"Data error: Invalid answer from deezer API searching from id '{id}'")
        return None
    
    return result




def get_playlist_in_cache(id):
    if id in playlist_cache:
        return playlist_cache[id]
    else:
        return None