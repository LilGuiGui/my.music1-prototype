import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def read_spotify_credentials():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # absolute path cuz wtf is 
    credentials_path = os.path.join(script_dir,"config", "credentials.txt")     # FileNotFoundError: [Errno 2] No such file or directory: 
                                                                                # RAAAAAAAAHHHHHHHHHHHHHH
    with open(credentials_path, "r") as f:
        client_id = f.readline().strip()
        client_secret = f.readline().strip()
    
    if not client_id or not client_secret:
        raise ValueError("Missing client_id or client_secret in credentials")
    
    return client_id, client_secret
