
import logging
import traceback
from typing import Dict, Iterator, List
import urllib3
import xmltodict

from Episode import Episode, Image, Blank
from util import *

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
        cover_image = self._download_cover(manifest)
        return self._episodes(manifest, cover_image)

    def _episodes(self, manifest: dict, cover_image: Image) -> Iterator['Episode']:
        author: str = self.author if self.author else dict['rss']['channel']['title']
        album: str = self.series if self.series else author

        episodes: List(dict) = manifest['rss']['channel']['item']

        for episode_blob in episodes :
            episode = Episode.create(author, album, episode_blob, cover_image)
            if episode and not isinstance(episode, Blank):
                yield episode
            elif not episode:
                logging.warning(F"Something was wrong with {author} - {album} - {episode_blob['title']}")
            continue

    def _download_cover(self, manifest: dict) -> Image:
        try:
            image_url = manifest['rss']['channel']['image']['url']

            with urllib3.PoolManager() as http:
                response = http.request('GET', image_url, preload_content=False)
                image_data: bytes = response.data
                image_type: str = response.headers['Content-Type']
            return Image(data=image_data, type=image_type)
        except:
            logging.warning(F"Failed to retrieve cover image for {str(self)}")
            logging.debug(traceback.format_exc())
            set_error(1)
        return None

    def _get_manifest(self) -> Dict:
        with urllib3.PoolManager() as http:
            response = http.request('GET', self.url, preload_content=False)
            try:
                data: dict = xmltodict.parse(response.data)
            except:
                logging.error(F"Failed to parse xml from {url}")
                logging.debug(traceback.format_exc())
                set_error(1)

        return data

    def _folder(self):
        if self.series and self.series != self.author:
            return F"{sanitise_path(self.author)}/{sanitise_path(self.series)}"
        return sanitise_path(F"{self.author}")

    def __eq__(self, other):
        return (
        self.url == other.url and
        self.author == other.author and
        self.series == other.series
        )

    def __str__(self):
        return self._folder()
