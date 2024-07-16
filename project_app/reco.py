import os
import difflib

from credentials import read_spotify_credentials
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def load_genre():
    get_path = os.path.dirname(os.path.abspath(__file__))         
    path_genre = os.path.join(get_path, "genres.MD")  

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
    match = difflib.get_close_matches(user_input, genre, n=3, cutoff=0.5) 
    print(f'Do you mean {match}?')

def get_spotify_recommendations(genre):
    client_id, client_secret = read_spotify_credentials()                                                                          
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) 

    results = sp.recommendations(seed_genres=[genre], limit=10)

    recommendations = []
    for track in results['tracks']:
        recommendations.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        })
    return recommendations

def getmy():
    genre = load_genre()
    
    while True:
        user_input = input("Enter a genre : ")
        user_input = user_input.lower()
        if user_input in genre:
            print(f'You Choose {user_input}')
            recommendations = get_spotify_recommendations(user_input)
            
            print("\nSong Recomendation:")
            for i, track in enumerate(recommendations, 1):
                print(f"{i}. {track['name']} by {track['artist']}")
            
            break
        else:
            find_closest_match(genre, user_input)
            
        
if __name__ == "__main__":
    getmy()