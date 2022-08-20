from base_scrapper import BaseScrapper
from bs4 import BeautifulSoup as bs, ResultSet
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotipy docs: https://spotipy.readthedocs.io/en/master/#

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
            print("Found same number of bands and songs repertory. Continue process...")
            self.iterate_through_bands_and_songs(bands, songs_lists)
        else:
            print("Could not find same number of bands and songs, abort process. Check html's source.")

    def iterate_through_bands_and_songs(self, bands:ResultSet, songs_lists:ResultSet):
        for (band, songs_list) in zip(bands, songs_lists):
            songs = []
            for song in songs_list:
                songs.append(song.text)
            self.dict_bands[band.text] = songs

if __name__ == "__main__":
    scrapper = BauhausScrapper("https://rockbarbauhaus.com/about/song-list/")
    scrapper.extract_bands_and_songs()
    print(1)