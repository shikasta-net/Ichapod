
import logging
import traceback
from typing import Dict, Iterator, List
import urllib3
from urllib3.exceptions import MaxRetryError
import xmltodict
from xml.parsers.expat import ExpatError

from Episode import Episode, Image, Blank
from util import *

class Podcast:

    def __init__(self, url: str, author: str = None, series: str = None):
        self.url = url
        self.author = author
        self.series = series

    @classmethod
    def create(cls, input: dict) -> 'Podcast':
        if not input.pop('enabled', True):
            return None

        return cls(**input)

    def episodes(self) -> Iterator['Episode']:
        manifest = self._get_manifest()
        if not manifest:
            return iter([])
        cover_image = self._download_cover(manifest)
        return self._episodes(manifest, cover_image)

    def _episodes(self, manifest: dict, cover_image: Image) -> Iterator['Episode']:
        if not self.series:
            self.series = manifest['rss']['channel']['title']
        author: str = self.author or self.series 

        episodes: List[dict] = manifest['rss']['channel']['item']

        for episode_blob in episodes :
            episode = Episode.create(author, self.series, episode_blob, cover_image)
            if episode and not isinstance(episode, Blank):
                yield episode
            elif not episode:
                logging.warning(F"Something was wrong with {author} - {self.series} - {episode_blob['title']}")

    def _download_cover(self, manifest: dict) -> Image:
        if 'image' in manifest['rss']['channel']:
            try:
                image_url = manifest['rss']['channel']['image']['url']

                with urllib3.PoolManager(
                    headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) ..'}
                ) as http:
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
        try:
            with urllib3.PoolManager(
                headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) ..'},
            ) as http:
                response = http.request('GET', self.url, preload_content=False)
                data: dict = xmltodict.parse(response.data)
                return data
        except MaxRetryError as e:
            logging.error(F"Unable to retrieve manifest from {self.url}: {e.reason}")
            logging.debug(traceback.format_exc())
            set_error(1)
        except ExpatError as e:
            logging.error(F"Failed to parse xml from {self.url}: {e}")
            logging.debug(traceback.format_exc())
            set_error(1)
        return {}

    def _folder(self):
        if self.author and self.series != self.author:
            return F"{sanitise_path(self.author)}/{sanitise_path(self.series)}"
        return sanitise_path(F"{self.series}")

    def __eq__(self, other):
        return (
        self.url == other.url and
        self.author == other.author and
        self.series == other.series
        )

    def __str__(self):
        return self._folder()
