import os
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials

def read_spotify_credentials():
    get_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_config = os.path.join(get_path, "config", "credentials.json")

    with open(path_config, 'r') as file:
        data = json.load(file)
    
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    if not client_id or not client_secret:
        raise ValueError("Missing client_id or client_secret in credentials")
    
    return client_id, client_secret
