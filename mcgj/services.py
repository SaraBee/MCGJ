import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup


class SpotifyClient:
    def __init__(self):
        auth_manager = SpotifyClientCredentials()
        self.spotipy = spotipy.Spotify(auth_manager=auth_manager)

    def isSpotifyTrack(self, url):
        return 'open.spotify.com' in url if url else False

    def getTrackInfo(self, url):
        track = self.spotipy.track(url)
        title = track['name']
        artist = track['artists'][0]['name']
        art_url = track['album']['images'][0]['url']
        return title, artist, art_url

    def getTrackArt(self, url):
        track = self.spotipy.track(url)
        art_url = track['album']['images'][0]['url']
        return art_url

    def getNonSpotifyArtwork(self, track):
        title = track.title if track.title else ''
        artist = track.artist if track.artist else ''
        query = title + ' ' + artist
        results = self.spotipy.search(query, type='track')
        if results['tracks']['items']:
            return results['tracks']['items'][0]['album']['images'][0]['url']
        return ''


class BandcampClient:
    def __init__(self):
        return

    def isBandcampTrack(self, url):
        return 'bandcamp.com' in url if url else False

    def getTrackInfo(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            name_section = soup.find(attrs={"id": "name-section"})

            title = name_section.find(attrs={"itemprop": "name"}).text.strip()
            artist = name_section.find(attrs={"itemprop": "byArtist"}).text.strip()
            art_url = soup.find("img", {"itemprop": "image"})["src"]
        except:
            print("Could not extract info from Bandcamp.")
            print(url)
            return None, None, None

        return title, artist, art_url
