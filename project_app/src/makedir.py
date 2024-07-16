import os

def check_dir():
    
    home_dir = os.path.expanduser("~") 
    directory = "downloaded_song"
    path = os.path.join(home_dir, "Music", directory)

    try:
        os.makedirs(path, exist_ok=True)
        return path
    except OSError as err:
        print(f"Error creating directory '{path}': {err}")
        return None

#Credits
#1. https://www.geeksforgeeks.org/python-os-path-expanduser-method/
