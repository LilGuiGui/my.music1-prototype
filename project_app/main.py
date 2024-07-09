import os
import logging
import spotipy
import yt_dlp as ytd
from savify import Savify
from spotipy.oauth2 import SpotifyClientCredentials
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
from makedir import check_dir

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path = check_dir()

def download_youtube(url, output_path):
    ydl_opts = {
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
        #moji app btw you can access if you have 
        client_credentials_manager = SpotifyClientCredentials(
            client_id="c2143c4a0d2243858b590723a4f8ddfd",
            client_secret="655b0c291f8048e3aad2b268a3a88bb1"
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        track_info = sp.track(url)
        print(f"Successfully retrieved info for track: {track_info['name']}")

        s = Savify(
            api_credentials=("c2143c4a0d2243858b590723a4f8ddfd", "655b0c291f8048e3aad2b268a3a88bb1"),
            quality=Quality.BEST,
            download_format=Format.MP3,
            path_holder=PathHolder(downloads_path=output_path),  
            group='%artist%/%album%',
            skip_cover_art=False,
        )
        s.download(url)
        
def main():
    if not path:
        logging.error("Failed to create or access the directory.")
        return

    while True:
        print("\nChoose a platform:")
        print("1. YouTube")
        print("2. Spotify")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == '3':
            logging.info("Exiting the program.")
            break
        
        url = input("Enter the URL of the song or playlist: ")
        
        if choice == '1':
            try:
                download_youtube(url, path)
                logging.info("YouTube download completed successfully.")
            except Exception as e:
                logging.error(f"Error downloading from YouTube: {e}")
        elif choice == '2':
            try:
                download_spotify(url, path)
                logging.info("Spotify download completed successfully.")
            except Exception as e:
                logging.error(f"Error downloading from Spotify: {e}")
        else:
            logging.warning("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()