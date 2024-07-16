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
    print(f'Do you mean {match}?')

def get_spotify_recommendations(genre):

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
        'url': track['external_urls']['spotify']
    }
    for track in listsong['tracks']]
    return recommendations  

def getmy():
    genre = load_genre()
    
    while True:
        print("Enter a genre")
        user_input = input("> ")
        user_input = user_input.lower()
        if user_input in genre:
            print(f'\nYou Choose {user_input}')
            recommendations = get_spotify_recommendations(user_input)
            
            print("\n10 Song Recomendations:")
            for i, track in enumerate(recommendations, 1):
                print(f"{i}. {track['name']} by {track['artist']}")

            print("\nDo you want to download a song from this list? (yes/no): ")
            download_choice = input("> ")
            download_choice = download_choice.lower()

            if download_choice == 'yes' or download_choice == 'y':
                while True:
                        song_number = int(input("Enter the number of the song you want to download: "))
                        if 1 <= song_number <= len(recommendations):
                            selected_song = recommendations[song_number - 1]
                            print("----------------------------------------")
                            print(f"Selected\n>> {selected_song['name']} by {selected_song['artist']}")
                            print("----------------------------------------")
                            return selected_song['url']
                        else:
                            print("Invalid Choice")
            else:
                print("No song selected for download.")
                return None
        else:
            find_closest_match(genre, user_input)

#Credits
#1. Thank you Abel, @asico for helping me