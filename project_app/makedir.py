import os

def check_dir():
    home_dir = os.path.expanduser("~")
    directory = "saved_song"
    path = os.path.join(home_dir, "Music", directory)

    try:
        os.makedirs(path, exist_ok=True)
        return path
    except OSError as error:
        print(f"Error creating directory '{path}': {error}")
        return None