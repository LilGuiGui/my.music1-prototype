import os

import yt_dlp as ytd

from savify import Savify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from savify.types import Quality, Format
from savify.utils import PathHolder


from makedir import check_dir
from credentials import read_spotify_credentials

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

def download_spotify(url, output_path):
    client_id, client_secret = read_spotify_credentials()            # for template, use my Moji/Lilgui personal API                                                                
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #CHECK THIS PART

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

def downloadinterface():
    path = check_dir()
    if not path:
        print("Failed to access your files.")
        return

    while True:
        print("Platform:")
        print("1. YouTube")
        print("2. Spotify")
        
        choice = input("> ")
        
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