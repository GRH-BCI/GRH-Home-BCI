import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import json

with open("spotify.json", "r") as spotify_config:
    config = json.load(spotify_config)
client_id = config["client_id"]
client_secret = config["client_secret"]
redirect_uri = config["redirect_uri"]


scope = "user-read-playback-state,user-modify-playback-state"


def spotify_handler(input_str: str):
    sp = spotipy.Spotify(
                            auth_manager=spotipy.SpotifyOAuth(
                             client_id=client_id,
                             client_secret=client_secret,
                             redirect_uri=redirect_uri,
                             scope=scope, open_browser=False))
    if input_str == "play":
        try:
            sp.start_playback()
        except:
            print("already playing")
    elif input_str == "pause":
        try:
            sp.pause_playback()
        except:
            print("already paused")
    elif input_str == "PorP":
        try:
            sp.start_playback()
        except:
            sp.pause_playback()
    elif input_str == "next":
        sp.next_track()

    elif input_str == "previous":
        sp.previous_track()


