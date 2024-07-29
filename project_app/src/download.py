import os
import yt_dlp as ytd
from savify import Savify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from savify.types import Quality, Format
from savify.utils import PathHolder
from makedir import check_dir
from credentials import read_spotify_credentials

def download_youtube(url, output_path, progress_callback=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: youtube_progress_hook(d, progress_callback)] if progress_callback else [],
    }
    
    with ytd.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def youtube_progress_hook(d, callback):
    if d['status'] == 'downloading':
        try:
            percent = float(d.get('_percent_str', '0%').replace('%', ''))
        except ValueError:
            percent = 0
        callback(percent, f"Downloading: {d.get('_percent_str', '0%')}")
    elif d['status'] == 'finished':
        callback(100, "Download finished, now converting...")

def download_spotify(url, output_path, progress_callback=None):
    client_id, client_secret = read_spotify_credentials()
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    track_info = sp.track(url)
    if progress_callback:
        progress_callback(0, f"Downloading: {track_info['name']}")

    s = Savify(
        api_credentials=(client_id, client_secret),
        quality=Quality.BEST,
        download_format=Format.MP3,
        path_holder=PathHolder(downloads_path=output_path),
        skip_cover_art=False,
    )
    s.download(url)
    
    if progress_callback:
        progress_callback(100, "Download completed")

def download_interface(url, platform, progress_callback=None):
    path = check_dir()
    if not path:
        raise Exception("Cannot access download directory")

    if platform == "YouTube":
        download_youtube(url, path, progress_callback)
    elif platform == "Spotify":
        download_spotify(url, path, progress_callback)
    else:
        raise ValueError("Invalid platform. Choose 'YouTube' or 'Spotify'.")