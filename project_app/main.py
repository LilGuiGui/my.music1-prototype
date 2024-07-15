import os

import yt_dlp as ytd

from savify import Savify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from savify.types import Quality, Format
from savify.utils import PathHolder

from makedir import check_dir

def download_youtube(url, output_path):
    ydl_opts = {                                                    #kwargs may differ, sesuai kebutuhan
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }
    
    with ytd.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def read_spotify_credentials():
    script_dir = os.path.dirname(os.path.abspath(__file__))         # absolute path cuz wtf is 
    credentials_path = os.path.join(script_dir, "credentials.txt")  # FileNotFoundError: [Errno 2] No such file or directory: 
                                                                    # RAAAAAAAAHHHHHHHHHHHHHH
    with open(credentials_path, "r") as f:
        client_id = f.readline().strip()
        client_secret = f.readline().strip()
    
    if not client_id or not client_secret:
        raise ValueError("Missing client_id or client_secret in credentials file")
    
    return client_id, client_secret

def download_spotify(url, output_path):
    client_id, client_secret = read_spotify_credentials()            # for template, use my Moji/Lilgui personal API                                                                
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #CHECK THIS PART YO

    track_info = sp.track(url)
    print(f"Successfully retrieved info for track: {track_info['name']}")

    s = Savify(
        api_credentials=(client_id, client_secret),
        quality=Quality.BEST,
        download_format=Format.MP3,
        path_holder=PathHolder(downloads_path=output_path),  
        skip_cover_art=False,
    )
    s.download(url)

def main():
    path = check_dir()
    if not path:
        print("Failed to create or access the directory.")
        return

    while True:
        print("\nChoose a platform:")
        print("1. YouTube")
        print("2. Spotify")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == '3':
            print("Exiting the program.")
            break
        
        url = input("Enter the URL of the song or playlist: ")
        
        if choice == '1':
            try:
                download_youtube(url, path)
                print("YouTube download completed successfully.")
            except Exception as e:
                print(f"Error downloading from YouTube: {e}")
        elif choice == '2':
            try:
                download_spotify(url, path)
                print("Spotify download completed successfully.")
            except Exception as e:
                print(f"Error downloading from Spotify: {e}")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()