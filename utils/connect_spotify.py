import spotipy
import webbrowser
import json

with open("spotify.json", "r") as spot_config_file:
    spot_config = json.load(spot_config_file)
spotify_client_ID = spot_config['client_id']
spotify_client_secret = spot_config['client_secret']
spotify_redirect_url = spot_config['redirect_uri']


scope = "user-read-playback-state,user-modify-playback-state"
def connect_spotify():
    try:
        sp = spotipy.Spotify(
                auth_manager=spotipy.SpotifyOAuth(
                  client_id=spotify_client_ID,
                  client_secret=spotify_client_secret,
                  redirect_uri=spotify_redirect_url,
                  scope=scope, open_browser=False))
    except:
        print('could not connect')

