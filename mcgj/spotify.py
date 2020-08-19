import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

class Spotify:
    def __init__(self):
        auth_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def getTrackInfo(self, url):
        track = self.sp.track(url)
        title = track['name']
        artist = track['artists'][0]['name']
        return title, artist


