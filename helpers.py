import requests
import base64
import os
from dotenv import load_dotenv
import urllib
from thefuzz import fuzz
import re

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



   
def get_id_from_url(url, type):
    type = type + "/"
    if type in url:
        print(f"playlist_id = {url.split(type)[1].split("?")[0]}")
        return url.split(type)[1].split("?")[0]
    return None # error return
# REFACTOR ==============================================================================================================================================================================
    
    
    
    
def get_tracklist(url):
    if "spotify" in url:
        return get_spotify_tracklist(url)
    elif "deezer" in url:
        return get_deezer_tracklist(url)
    else:
        return None
    
    

'''
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
    if not id:
        print("Could not get id from url")
        return None
    
    api_url = f"https://api.spotify.com/v1/{collection}s/{id}"
        
    header = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json"
        }
    
    id_counter = 1
    playable_tracks = []
    options_tracks = []
    total_tracks = 0
    first_call = True
    
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
        if first_call:
            collection_image = data.get("images", [{}])[0].get("url")
            total_tracks = track_page.get("total", 0)
            first_call = False
        
        items = track_page.get('items', [])
        
        for item in items:
            track_data = item.get('track') if 'track' in item else item
            
            if not track_data:
                continue
            
            image_url = None
            if collection == "album":
                image_url = collection_image if collection_image else "/static/images/default_cover.png"
            else:
                album_images = track_data.get("album", {}).get("images", []) 
                image_url = album_images[0].get("url") if album_images else "/static/images/default_cover.png"
            
            options_track = {
                "id": id_counter,
                "title": track_data.get("name"),
                "image": image_url
            }
            options_tracks.append(options_track)
            
            preview = track_data.get("preview_url")
            if not preview:
                artists = [artist["name"] for artist in track_data.get("artists", [])]
                preview = get_preview_from_deezer(track_data.get("name"), artists)
            
            if preview:
                playable_track = {
                    "id": id_counter,
                    "preview": preview

                }
                playable_tracks.append(playable_track)
            
            id_counter += 1
            
        api_url = track_page.get("next")
        print(f"next field = {api_url}")
        
    print(f"Length of total tracks get from spotify: {len(options_tracks)}")
    print(f"Length of playable tracks get from spotify: {len(playable_tracks)}")
    #print(f"called URL: {url}")

    return {"playable_tracks": playable_tracks, "options_tracks": options_tracks, "total_tracks": total_tracks}
'''




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
    if not id:
        print("Could not get id from url")
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
        print(f"Error at first spotify API call: {e}")
        return None
    
    playable_tracks, options_tracks = [], []
    id_counter, total_tracks = 1, 0
    first_call = True
    
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
        
        if first_call:
            total_tracks = data.get("total", 0)
            first_call = False
        
        for item in data.get("items", []):
            track_data = item.get("track") if "track" in item else item
            
            if not track_data or not track_data.get("name"):
                continue
            
            image_url = album_cover_url if collection == "album" else None
            if not image_url:
                track_album_images  = track_data.get("album", {}).get("images", []) 
                image_url = track_album_images [0].get("url") if track_album_images else "/static/images/default_cover.png"
            
            options_track = {
                "id": id_counter,
                "title": track_data.get("name"),
                "image": image_url
            }
            options_tracks.append(options_track)
            
            preview = track_data.get("preview_url")
            if not preview:
                artists_list = track_data.get("artists", [])
                artist = artists_list[0].get("name") if len(artists_list) > 0 else None
                preview = get_preview_from_deezer(track_data.get("name"), artist)
            
            if preview:
                playable_track = {
                    "id": id_counter,
                    "preview": preview
                }
                playable_tracks.append(playable_track)
            
            id_counter += 1
            
        api_url = data.get("next")
        #print(f"next field = {api_url}")
        
    print(f"Length of total tracks get from spotify: {len(options_tracks)}")
    print(f"Length of playable tracks get from spotify: {len(playable_tracks)}")
    #print(f"called URL: {url}")

    return {"playable_tracks": playable_tracks, "options_tracks": options_tracks, "total_tracks": total_tracks}




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
            print(f"Error at deezer API request. {e}")
            return None
        except ValueError:
            print(f"Error at processing data from the deezer API")
            return None
        
        if first_call == True:
            total_tracks = data.get("nb_tracks")
            if collection == "album":
                album_cover = data.get("cover_medium", "/static/images/default_cover.png")
            
        track_source = data.get("tracks", data)
        items_list = track_source.get("data", [])
            
        for track_data in items_list:
            if not track_data:
                continue
            
            options_track = {
                "id": id_counter,
                "title": track_data.get("title"),
                "image": track_data.get("album", {}).get("cover_medium", "/static/images/default_cover.png") if collection == "playlist" else album_cover
            }
            options_tracks.append(options_track)
            
            preview_url = track_data.get("preview")
            if preview_url:
                playable_track = {
                    "id": id_counter,
                    "preview": preview_url
                }
                playable_tracks.append(playable_track)
            
            id_counter += 1
        
        api_url = data.get("next")
        first_call = False
        
    print(f"Length of total tracks get from deezer: {len(options_tracks)}")
    print(f"Length of playable tracks get from deezer: {len(playable_tracks)}")
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
    
    
    
    
    
def get_preview_from_deezer(title, primary_artist):
    if not primary_artist:
        print(f"Not found artist to music '{primary_artist}'")
        return None
    
    normalized_spotify_title = _normalize_title(title)
    
    safe_title = urllib.parse.quote_plus(title)
    safe_artist = urllib.parse.quote_plus(primary_artist)
    
    api_url = f'https://api.deezer.com/search?q=track:"{safe_title}"artist:"{safe_artist}"'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("data", [])
        if not search_results:
            print(f"Spotify music '{title}' for artist {primary_artist} could not find a deezer version")
            return None

        best_match = None
        highest_score = -1
        
        for item in search_results:
            deezer_title = item.get("title", "")
            normalized_deezer_title = _normalize_title(deezer_title)
            
            score = fuzz.ratio(normalized_spotify_title, normalized_deezer_title)
            
            if score > highest_score:
                highest_score = score
                best_match = item
                
        CONFIDENCE_THRESHOLD = 85
        if highest_score >= CONFIDENCE_THRESHOLD:
            #print(f"    -> Best match found ({highest_score}%). '{best_match.get("title")}'")
            return best_match.get("preview")
        else:
            #if best_match:
                #print(f"    -> Best match found ({highest_score}%), but under the confidence threshold. '{best_match.get("title")}'")
            print(f"Title of spotify music not found in deezer: '{title}' for artist: {primary_artist}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: could not search for {title} in deezer. {e}")
        return None
    except ValueError:
        print(f"Data error: Invalid answer from deezer API searching from {title}")
        return None