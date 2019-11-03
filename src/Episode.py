
import collections
import logging
import mimetypes
import mutagen
from pathlib import Path
import traceback

from util import *

mimetypes.add_type('audio/mp3', '.mp3')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/x-m4a', '.m4a')

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
    def create(cls, episode_number: int, author: str, album: str, episode: dict) -> 'Episode':
        try:
            url = episode['enclosure']['@url']
            if not url:
                return None

            logging.debug(F"Creating episode from { dict({ part:episode[part] for part in ['enclosure', 'title', 'pubDate', 'guid'] }, **{'number':episode_number, 'author':author, 'album': album}) }")

            guid = episode['guid']['#text'] if type(episode['guid']) == collections.OrderedDict else episode['guid']

            return cls(
                url = url,
                number = episode_number,
                title = remove_unicode(episode['title']),
                author = remove_unicode(author),
                album = remove_unicode(album),
                date = convert_date(episode['pubDate']),
                type = cls._guess_extension(episode['enclosure']['@type'], url),
                guid = guid
            )
        except KeyError as e:
            logging.warning(F"Unable to find key {e} while creating Episode {episode_number} - {author} - {album}")

        return None

    @classmethod
    def load(cls, file_path: Path) -> 'Episode':
        file_string = str(file_path)
        try:
            audio = mutagen.File(file_string, easy=True)

            return cls(
                url = audio['website'][0],
                number = audio['tracknumber'][0],
                title = audio['title'][0],
                author = audio['artist'][0],
                album = audio['album'][0],
                date = convert_date(audio['date'][0]),
                type = file_path.suffix,
                guid = audio['catalognumber'][0]
            )
        except:
            logging.error(F"Failed to load file {file_path}")
            logging.debug(traceback.format_exc())
        return None

    def download(self, base_path: Path) -> Path:
        podcast_file = base_path / str(self)
        podcast_file.touch()
        return podcast_file

    @classmethod
    def _guess_extension(cls, mimetype: str, url: str) -> str:
        extensions =  mimetypes.guess_all_extensions(mimetype)
        logging.debug(F"Getting extentions {extensions} from {mimetype}")

        matches = [ extension for extension in extensions if extension in url ]
        logging.debug(F"Of which {matches} matchs {url}")

        if len(matches) == 1:
            return matches[0]

        return extensions[0]

    def _filename(self) -> str:
        return sanitise_path(F"{self.date} - {self.title} - {self.author} - {self.album}{self.type}")

    def __eq__(self, other):
        if not other:
            return False
        logging.debug(F"Comparing to another file {(self.url, other.url, self.url == other.url)} and {(self.number, other.number, self.number == other.number)} and {(self.title, other.title, self.title == other.title)} and {(self.author, other.author, self.author == other.author)} and {(self.album, other.album, self.album == other.album)} and {(self.date, other.date, self.date == other.date)} and {(self.extension, other.extension, self.extension == other.extension)} and {(self.guid, other.guid, self.guid == other.guid)}")
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
