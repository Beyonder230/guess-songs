import requests
import base64
import os
from dotenv import load_dotenv
import urllib

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
    playable_tracks = []
    options_tracks = []
    
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
            
            options_track = {
                "id": id_counter,
                "title": track_data.get("name"),
                "image": track_data.get("album", {}).get("images", [{}])[0].get("url") if "album" in track_data else data.get("images", [{}])[0].get("url")
            }
            options_tracks.append(options_track)
            
            preview = track_data.get("preview_url")
            if not preview:
                artists = [artist["name"] for artist in track_data.get("artists", [])]
                preview = get_preview_from_deezer(track_data.get("name"), artists)
                if not preview:
                    id_counter += 1
                    continue
            
            playable_track = {
                "id": id_counter,
                "preview": preview

            }
            playable_tracks.append(playable_track)
            
            id_counter += 1
            
        api_url = track_page.get("next")
        
    print(f"Length of total tracks get from spotify: {len(options_tracks)}")
    print(f"Length of playable tracks get from spotify: {len(playable_tracks)}")
    #print(f"called URL: {url}")

    return {"playable_tracks": playable_tracks, "options_tracks": options_tracks}




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
        
        if first_call == True and collection == "album":
            album_cover = data.get("cover_medium")
            first_call = False
            
        track_source = data.get("tracks", data)
        items_list = track_source.get("data", [])
            
        for track_data in items_list:
            if not track_data:
                continue
            
            options_track = {
                "id": id_counter,
                "title": track_data.get("title"),
                "image": track_data.get("album", {}).get("cover_medium") if collection == "playlist" else album_cover
            }
            options_tracks.append(options_track)
            
            preview_url = track_data.get("preview")
            if not preview_url:
                id_counter += 1
                continue

            playable_track = {
                "id": id_counter,
                "preview": preview_url
            }
            playable_tracks.append(playable_track)
            
            id_counter += 1
            
        api_url = data.get("next")
        
    print(f"Length of total tracks get from deezer: {len(options_tracks)}")
    print(f"Length of playable tracks get from deezer: {len(playable_tracks)}")
    #print(f"called URL: {url}")

    return {"playable_tracks": playable_tracks, "options_tracks": options_tracks}




def get_preview_from_deezer(title, artists):
    for artist in artists:
        safe_title = urllib.parse.quote_plus(title)
        safe_artist = urllib.parse.quote_plus(artist)
        
        api_url = f'https://api.deezer.com/search?q=track:"{safe_title}"artist:"{safe_artist}"'
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            search_results = data.get("data")

            if len(search_results) > 0:
                for item in search_results:
                    if item.get("title", "").strip().upper() == title.strip().upper():
                        return item.get("preview")
        except requests.exceptions.RequestException as e:
            print(f"Request error: could not search for {title} in deezer. {e}")
            return None
        except ValueError:
            print(f"Data error: Invalid answer from deezer API searching from {title}")
            continue
    return None