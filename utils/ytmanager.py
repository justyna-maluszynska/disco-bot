from ytmusicapi import YTMusic

class YTManager():
    def __init__(self) -> None:
        self._ytmusic = YTMusic()

    def play(self, song_name):
        search_results = self._ytmusic.search()