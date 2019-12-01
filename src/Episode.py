
import collections
import logging
import mimetypes
import mutagen
from mutagen import easymp4
from pathlib import Path
import r128gain
import shutil
import traceback
import urllib3

from util import *

mimetypes.add_type('audio/mp3', '.mp3')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/x-m4a', '.m4a')

mutagen.easymp4.EasyMP4Tags.RegisterTextKey('catalognumber','egid')
mutagen.easymp4.EasyMP4Tags.RegisterTextKey('website','purl')

class Episode:

    def __init__(self, url: str, number: int, title: str, author: str, album: str, date: str, extension: str, guid: str):
        self.url = url
        self.number = int(number)
        self.title = title
        self.author = author
        self.album = album
        self.date = date
        self.extension = extension
        self.guid = guid

    @classmethod
    def create(cls, episode_number: int, author: str, album: str, episode: dict) -> 'Episode':
        try:
            url = episode['enclosure']['@url']
            if not url:
                return None

            logging.debug(F"Creating episode from { dict({ part:episode[part] for part in ['enclosure', 'title', 'pubDate', 'guid'] }, **{'number':episode_number, 'author':author, 'album': album}) }")

            guid = episode['guid']['#text'] if type(episode['guid']) == collections.OrderedDict else episode['guid']

            title = clean_title(episode['title'])
            author = remove_unicode(author)
            album = remove_unicode(album)
            date = convert_date(episode['pubDate'])
            extension = cls._guess_extension(episode['enclosure']['@type'], url)

            if guid and episode_number and title and author and album and date and url and extension :
                return cls(url, episode_number, title, author, album, date, extension, guid)
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
                extension = file_path.suffix,
                guid = audio['catalognumber'][0]
            )
        except:
            logging.error(F"Failed to load file {file_path}")
            logging.debug(traceback.format_exc())
        return None

    def download_to(self, base_path: Path) -> Path:
        podcast_file = base_path / str(self)

        logging.info(F"Downloading {podcast_file.name}")

        self._download(self.url, to=podcast_file)
        self._tag_episode(podcast_file)
        self._replay_gain(podcast_file)

        return podcast_file if podcast_file.exists() else None

    @classmethod
    def _guess_extension(cls, mimetype: str, url: str) -> str:
        extensions =  mimetypes.guess_all_extensions(mimetype)
        logging.debug(F"Getting extentions {extensions} from {mimetype}")

        matches = [ extension for extension in extensions if extension in url ]
        logging.debug(F"Of which {matches} matchs {url}")

        if len(matches) == 1:
            return matches[0]

        return extensions[0]

    @staticmethod
    def _download(url: str, to: Path) :
        logging.debug(F"Downloading {url} to {to}")

        with urllib3.PoolManager() as http:
            try:
                with http.request('GET', url, preload_content=False) as response, open(to, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except:
                logging.error(F"Failed to download {url} to {to}")
                logging.debug(traceback.format_exc())

    @staticmethod
    def _replay_gain(podcast_file: Path) :
        if podcast_file.exists() :
            logging.debug(F"Compute replay gain of {podcast_file}")

            error = r128gain.process([str(podcast_file)])
            if error > 0 :
                raise Exception(F"Unable to process gain on {podcast_file}")

    def _tag_episode(self, podcast_file: Path) :
        if podcast_file.exists() :
            metadata = mutagen.File(str(podcast_file), easy=True)
            metadata['album'] = self.album
            metadata['artist'] = self.author
            metadata['catalognumber'] = self.guid
            metadata['date'] = self.date
            metadata['genre'] = "Podcast"
            metadata['tracknumber'] = [str(self.number)]
            metadata['title'] = self.title
            metadata['website'] = self.url
            metadata.save()

    def _filename(self) -> str:
        by = self.author if self.album == self.author or not self.album else F"{self.author} - {self.album}"
        return sanitise_path(F"{self.date} - {self.title} - {by}{self.extension}")

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
        self.extension == other.extension and
        self.guid == other.guid
        )

    def __lt__(self, other):
        return self.date < other.date

    def __str__(self):
        return self._filename()
