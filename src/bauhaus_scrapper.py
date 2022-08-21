from http import client
import sys
from base_scrapper import BaseScrapper
from bs4 import BeautifulSoup as bs, ResultSet
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

# Spotipy docs: https://spotipy.readthedocs.io/en/master/#
# Tutorial: https://github.com/plamere/spotipy/blob/master/README.md

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

    def scrap_bands_and_songs(self, bands:ResultSet, songs_lists:ResultSet):
        for (band, songs_list) in zip(bands, songs_lists):
            songs = []
            for song in songs_list:
                songs.append(song.text)
            self.dict_bands[band.text] = songs

    def export_to_spotify(self):
        self.connect_to_spotify()
        return 1

    def connect_to_spotify(self):
        if len(sys.argv) > 3:
            username = sys.argv[1]
            client_id = sys.argv[2]
            client_secret = sys.argv[3]

            scope = 'playlist-modify-public'
            
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=f"http://localhost:8888/callback",
                                               scope="user-library-read"))

            results = sp.current_user_saved_tracks()
            for idx, item in enumerate(results['items']):
                track = item['track']
                print(idx, track['artists'][0]['name'], " – ", track['name'])
            # sp = spotipy.Spotify(auth=token)


            # auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            # sp = spotipy.Spotify(auth_manager=auth_manager)

            # playlist_name = f"Bauhaus Roppongi"
            # sp.user_playlist_create(username, name=playlist_name)
            # print(sp)
            # token = util.prompt_for_user_token(
            #     username, scope, 
            #     client_id=client_id, client_secret=client_secret, redirect_uri='http://localhost') 
            # sp = spotipy.Spotify(auth=token)
        else:
            print("Usage: %s username playlist_id track_id ..." % (sys.argv[0],))
            sys.exit()

if __name__ == "__main__":
    scrapper = BauhausScrapper("https://rockbarbauhaus.com/about/song-list/")
    scrapper.extract_bands_and_songs()
    scrapper.connect_to_spotify()
    print(1)