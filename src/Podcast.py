
from typing import Dict, Iterator, List
import urllib3
import xmltodict

from Episode import Episode

class Podcast:

    def __init__(self, url: str, author: str = None, series: str = None):
        self.url = url
        self.author = author
        self.series = series

    @classmethod
    def create(cls, input: str) -> 'Podcast':
        tokens = cls._tokanise(input)

        if not tokens:
            return None

        return cls(tokens[-1], *tokens[:-1])

    @classmethod
    def _tokanise(cls, input: str) -> List[str]:
        if input.lstrip()[0] == "#":
            return None
        return [ token.strip() for token in input.split("---") ]

    def episodes(self) -> Iterator['Episode']:
        manifest = self._get_manifest()
        return self._episodes(manifest)

    def _episodes(self, manifest: dict) -> Iterator['Episode']:
        author: str = self.author if self.author else dict['rss']['channel']['title']
        album: str = self.series if self.series else author

        episodes: List(dict) = manifest['rss']['channel']['item']

        episode_number = len(episodes)
        for episode_blob in episodes :
            episode = Episode.create(episode_number, author, album, episode_blob)
            episode_number -= 1
            if episode:
                yield episode
            continue

    def _get_manifest(self) -> Dict:
        http = urllib3.PoolManager()

        response = http.request('GET', self.url, preload_content=False)
        try:
            data: dict = xmltodict.parse(response.data)
        except:
            error(F"Failed to parse xml from {url} ({traceback.format_exc()})")

        return data


    def __eq__(self, other):
        return (
        self.url == other.url and
        self.author == other.author and
        self.series == other.series
        )

    def __str__(self):
        return F"{self.url}, {self.author}, {self.series}"