from base_scrapper import BaseScrapper
from bs4 import BeautifulSoup as bs, ResultSet

class BauhausScrapper(BaseScrapper):
    def __init__(self, url: str):
        super().__init__(url)

    def extract_bands_and_songs(self):
        soup = bs(self.return_content(), features='html.parser')  
        results = soup.find('div', class_="entry-content")
        bands = results.find_all('h4')
        songs = results.find_all('ul')
        if len(bands) == len(songs):
            print("Found same number of bands and songs repertory. Continue process...")
            self.iterate_through_bands_and_songs(bands, songs)
        else:
            print("Could not find same number of bands and songs, abort process. Check html's source.")

    def iterate_through_bands_and_songs(self, bands:ResultSet, songs:ResultSet):
        for (band, song) in zip(bands, songs):
            print(band)
            print(song)
            print(1)

if __name__ == "__main__":
    scrapper = BauhausScrapper("https://rockbarbauhaus.com/about/song-list/")
    scrapper.extract_bands_and_songs()
