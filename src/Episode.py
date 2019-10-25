

import logging
import mimetypes
from pathlib import Path

from util import *

class Episode:

    def __init__(self, url: str, number: int, title: str, author: str, album: str, date: str, type: str, guid: str):
        self.url = url
        self.number = int(number)
        self.title = title
        self.author = author
        self.album = album
        self.date = date
        self.type = type
        self.guid = guid

    @classmethod
    def create(cls, episode_number: int, author: str, album: str, episode: dict):
        try:
            if not episode['enclosure']['@url']:
                return None

            logging.debug(F"Creating episode from { dict({ part:episode[part] for part in ['enclosure', 'title', 'pubDate', 'guid'] }, **{'number':episode_number, 'author':author, 'album': album}) }")

            return cls(
                url = episode['enclosure']['@url'],
                number = episode_number,
                title = remove_unicode(episode['title']),
                author = remove_unicode(author),
                album = remove_unicode(album),
                date = convert_date(episode['pubDate']),
                type = mimetypes.guess_extension(episode['enclosure']['@type']),
                guid = episode['guid']
            )
        except KeyError as e:
            logging.warning(F"Unable to find key {e} while creating Episode {episode_number} - {author} - {album}")

        return None

    def download(self, base_path: Path) -> Path:
        podcast_file = base_path / str(self)
        podcast_file.touch()
        return podcast_file

    def _filename(self) -> str:
        return sanitise_path(F"{self.date} - {self.title} - {self.author} - {self.album}{self.type}")

    def __eq__(self, other):
        if not other:
            return False
        return (
        self.url == other.url and
        self.number == other.number and
        self.title == other.title and
        self.author == other.author and
        self.album == other.album and
        self.date == other.date and
        self.type == other.type and
        self.guid == other.guid
        )

    def __lt__(self, other):
        return self.date < other.date

    def __str__(self):
        return self._filename()
