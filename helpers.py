import requests
import random
import base64

def get_access():
    url = "https://accounts.spotify.com/api/token"
    client_id = ***REMOVED***
    client_secret = ***REMOVED***
    
    credentials = f"{client_id}:{client_secret}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    header = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"}
    
    body = "grant_type=client_credentials"
    
    response = requests.post(url, headers=header, data=body)
    
    print(f"acess_token variable: {response}")
    
    response_data = response.json()
    print(f"acess_token json: {response_data}")
    
    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        print("Token generating error", response_data)
        return None

def get_random_track(playlist_id, access):
    # http info
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    header = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json"
        }
    
    # trying to make a get resquest for playlist
    playlist_response = requests.get(url, headers=header)
    print(f"playlist_response variable: {playlist_response}")
    
    # trying to get the tracks of this playlist
    tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    print(f"called URL: https://api.spotify.com/v1/playlists/{playlist_id}/tracks")
    tracks_response = requests.get(tracks_url, headers=header)
    tracks = tracks_response.json()
    print(f"tracks json: {tracks}")
    
    if "error" in tracks:
        return "error"
    
    total_tracks = len(tracks["items"])
    checked_tracks = 0
    while checked_tracks < total_tracks:
        random_track = random.choice(tracks["items"])
        if random_track["track"]["preview_url"] != None:
            return random_track
        checked_tracks += 1
        
    return "There's no elligible track in the playlist"
    # currently this is an simple version of the function bc its only consider the first 50 tracks (ok for the top 50 global default playlist)
    
def get_id_from_url(url, type):
    type = type + "/"
    if type in url:
        print(f"playlist_id = {url.split(type)[1].split("?")[0]}")
        return url.split(type)[1].split("?")[0]
    return None # error return

def test_access(access_token):
    playlist_id = "09tJur2DIOM35bqoVXDjgw"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"  # Sem /tracks no final
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(response.status_code, response.json())  # Deve retornar 200 se a playlist for pública