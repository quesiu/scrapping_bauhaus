# Standard Python Libraries
import re
import sys
from datetime import date
from itertools import zip_longest
# Custom Libraries
from base_scrapper import BaseScrapper
# Librairies from pip
import unidecode
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup as bs, ResultSet
from fuzzywuzzy import fuzz

# Spotipy docs: https://spotipy.readthedocs.io/en/master/#
# Tutorial: https://github.com/plamere/spotipy/blob/master/README.md
# Use spotipy and BS to create Spotify playlist: https://towardsdatascience.com/using-python-to-create-spotify-playlists-of-the-samples-on-an-album-e3f20187ee5e

# Parameters to play with to raise/decrease accuracy and overall number of detected songs
QUERY_LIMIT = 10
PERCENTAGE_TOLERANCY_BAND = 90
PERCENTAGE_TOLERANCY_SONG = 65

def grouper(iterable, n):
        args = [iter(iterable)] * n
        return zip_longest(*args)

class BauhausScrapper(BaseScrapper):
    def __init__(self, url: str):
        super().__init__(url)
        self.dict_bands = {}

    def extract_bands_and_songs(self):
        soup = bs(self.return_content(), features='html.parser')
        results = soup.find('div', class_="entry-content")
        bands = results.find_all('h4')
        songs_lists = results.find_all('ul')
        if len(bands) == len(songs_lists):
            # print("Found same number of bands and songs repertory. Continue process...")
            self.scrap_bands_and_songs(bands, songs_lists)
        else:
            print("Could not find same number of bands and songs, abort process. Check html's source.")

    def remove_useless_title_info(self, title:str):
        # Matches anything between parenthesis at the end of a title (+ potential spaces) and remove it
        return re.sub(r'(.+)(\(.*\) *)$', r'\1', title)
        

    def scrap_bands_and_songs(self, bands:ResultSet, songs_lists:ResultSet):
        self.total_number_tracks = 0
        for (band, songs_list) in zip(bands, songs_lists):
            songs = []
            for song in songs_list:
                songs.append(self.remove_useless_title_info(song.text))
                self.total_number_tracks += 1
            self.dict_bands[band.text] = songs

    def export_to_spotify(self):
        self.connect_to_spotify()
        self.get_track_ids()
        self.create_playlist_with_songs()

    def connect_to_spotify(self):
        if len(sys.argv) > 3:
            self.username = sys.argv[1]
            client_id = sys.argv[2]
            client_secret = sys.argv[3]

            scope = 'playlist-modify-public'
            
            # Connect to Spotify via spotipy using Authorization Code Flow
            # Requires to connect account with https://developer.spotify.com/
            # to get Client ID and Secret (to be passed as arguments)
            # as well as adding http://localhost:8888/callback to Spotify dashboard's Redirect URIs
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=f"http://localhost:8888/callback",
                                               scope=scope))
        else:
            print("Usage: %s username playlist_id track_id ..." % (sys.argv[0],))
            sys.exit()

    def create_playlist_with_songs(self):
        # Create new playlist with current day in title; will NOT erase existing ones
        playlist_name = f"Bauhaus Roppongi (last updated {date.today()})"
        playlist_id = self.sp.user_playlist_create(self.username, name=playlist_name)
        # Get created playlist id
        playlist_id = playlist_id['id']
        
        # Add songs 100 by 100 because spotipy is limited by that
        tracks_groups = grouper(self.track_ids, 100)
        for tracks in tracks_groups:
            # Filter None items out
            tracks = list(filter(None, tracks))
            self.sp.user_playlist_add_tracks(self.username, playlist_id, tracks)

    def get_track_ids(self):
        track_ids = []

        for band, songs in self.dict_bands.items():
            for song in songs:
                # Remove potential space characters for bands (\xa0)
                band = unidecode.unidecode(band)
                # Use Spotify search API with artists and track name
                results = self.sp.search(q=f"{band} {song} ", limit=QUERY_LIMIT, type='track') #get 5 responses since first isn't always accurate
                if results['tracks']['total'] == 0: #if track isn't on spotify as queried, go to next track
                    print(f"Could not add following track: {band} - {song}")
                    continue
                else:
                    for j in range(len(results['tracks']['items'])):
                        current_querried_band = results['tracks']['items'][j]['artists'][0]['name']
                        current_querried_song = results['tracks']['items'][j]['name']
                        if fuzz.partial_token_set_ratio(current_querried_band, band) > PERCENTAGE_TOLERANCY_BAND and fuzz.partial_token_set_ratio(current_querried_song, song) > PERCENTAGE_TOLERANCY_SONG : #get right response by matching on artist and title
                            track_ids.append(results['tracks']['items'][j]['id']) #append track id
                            break #don't want repeats of a sample ex: different versions
                        else:
                            # print(f"Could not add following track: {band} - {song}")
                            continue
                    else:
                        print(f"Could not add following track: {band} - {song}")
        print("Got TrackIDs")
        print(f"Grasped a total of {len(track_ids)} tracks out of {self.total_number_tracks}")
        self.track_ids = track_ids


if __name__ == "__main__":
    scrapper = BauhausScrapper("https://rockbarbauhaus.com/about/song-list/")
    scrapper.extract_bands_and_songs()
    scrapper.export_to_spotify()