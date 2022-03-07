import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from config.config import CLIENT_ID, CLIENT_SECRET

spotify_api = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
)


class Spotify:
    def __init__(self):
        self.api = spotify_api

    def get_playlist_items_title(self, url):
        tracks = self.api.playlist_items(url)["items"]
        return list(map(lambda x: x["track"]["name"], tracks))
