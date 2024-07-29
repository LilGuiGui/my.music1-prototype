import os
import difflib

from credentials import read_spotify_credentials
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from download import download_spotify

def load_genre():

    get_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))         
    path_genre = os.path.join(get_path, "data", "genres.MD")  

    with open(path_genre, 'r') as file:
        return [line.strip().lower() for line in file]

def find_genre(genres, user_input):

    user_input = user_input.lower()
    if user_input in genres:
        return user_input
    else:
        return find_closest_match(genres, user_input)
    
def find_closest_match(genre, user_input):

    user_input = user_input.lower()
    match = difflib.get_close_matches(user_input, genre, n=5, cutoff=0.3) 
    return match
    
def get_spotify_recommendations_based_on_genre(genre):
    client_id, client_secret = read_spotify_credentials()                                                                          
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) 

    listsong = sp.recommendations(seed_genres=[genre], limit=10)
    recommendations = [
    {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'url': track['external_urls']['spotify'],
        'preview_url': track['preview_url'],
        'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None
    }
    for track in listsong['tracks']]
    return recommendations

def get_spotify_recommendations_based_on_artist(artist_name):
    client_id, client_secret = read_spotify_credentials()
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Search for the artist
    results = sp.search(q='artist:' + artist_name, type='artist')
    if not results['artists']['items']:
        return []  # Return empty list if artist not found

    artist_id = results['artists']['items'][0]['id']

    # Get recommendations based on artist ID
    listsong = sp.recommendations(seed_artists=[artist_id], limit=10)
    recommendations = [
    {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'url': track['external_urls']['spotify'],
        'preview_url': track['preview_url'],
        'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None
    }
    for track in listsong['tracks']]
    return recommendations

#Credits
#1. Thank you Abel, @asico for helping me