
import collections
import logging
import mimetypes
import mutagen
from mutagen import easymp4
from mutagen.id3 import APIC, PictureType, Encoding
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
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

    def __init__(self, url: str, number: int, title: str, author: str, album: str, date: str, extension: str, guid: str, cover_image: 'Image'=None):
        self.url = url
        self.number = int(number)
        self.title = title
        self.author = author
        self.album = album
        self.date = date
        self.extension = extension
        self.guid = guid
        self.cover_image = cover_image

    @classmethod
    def create(cls, author: str, album: str, episode: dict, cover_image: 'Image') -> 'Episode':
        try:
            url = episode['enclosure']['@url']
            if not url:
                return None

            logging.debug(F"Creating episode from { dict({ part:episode[part] for part in ['enclosure', 'title', 'pubDate', 'guid'] }, **{'author':author, 'album': album}) }")

            guid = episode['guid']['#text'] if type(episode['guid']) == collections.OrderedDict else episode['guid']

            title = clean_title(episode['title'])
            author = remove_unicode(author)
            album = remove_unicode(album)
            date = convert_date(episode['pubDate'])
            episode_number = tracknumber_from_date(date)
            extension = cls._guess_extension(episode['enclosure']['@type'], url)

            if guid and episode_number and title and author and album and date and url and extension :
                return cls(url, episode_number, title, author, album, date, extension, guid, cover_image)
        except KeyError as e:
            logging.warning(F"Unable to find key {e} while creating Episode of {author} - {album}")

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
            set_error(1)
        return None

    def download_to(self, base_path: Path) -> Path:
        podcast_file = base_path / str(self)

        logging.info(F"Downloading {podcast_file.name}")

        self._download(self.url, to=podcast_file)
        self._tag_episode(podcast_file)
        self._add_cover_image(self.cover_image, podcast_file)
        self._replay_gain(podcast_file)

        return podcast_file if podcast_file.exists() else None

    def serialise(self):
        return "\t".join([
            self.author,
            self.album,
            self.date,
            str(self.number),
            self.title,
            self.guid,
            self.extension,
            self.url,
        ])

    def lookup(self, record: list) -> bool:
        prefix = "\t".join([
            self.author,
            self.album,
            self.date,
            ])
        left_result = string_prefix_comparator_left(prefix)
        right_result = string_prefix_comparator_right(prefix)
        possible_matches = record[GenericBisect.bisect(record,left_result):GenericBisect.bisect(record,right_result)]
        for match in possible_matches:
            tok = match.split('\t')
            other = Episode(author=tok[0], album=tok[1], date=tok[2], number=tok[3], title=tok[4], guid=tok[5], extension=tok[6], url=tok[7])
            if other == self:
                return True
        return False

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
                with http.request('GET', url, preload_content=False, retries=10) as response, open(to, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except:
                logging.error(F"Failed to download {url} to {to}")
                logging.debug(traceback.format_exc())
                set_error(1)

    @staticmethod
    def _replay_gain(podcast_file: Path) :
        if podcast_file.exists() :
            logging.debug(F"Compute replay gain of {podcast_file}")

            error = r128gain.process([str(podcast_file)])
            if error > 0 :
                raise Exception(F"Unable to process gain on {podcast_file}")

    @staticmethod
    def _add_cover_image(cover_image: 'Image', podcast_file: Path) :
        if podcast_file.exists() and cover_image :
            metadata = mutagen.File(str(podcast_file), easy=False)
            if type(metadata) == MP3 and not metadata.tags.getall('APIC'):
                logging.info(F"Adding image tag")
                metadata.tags.add(
                    APIC(
                        data=cover_image.data,
                        mime=cover_image.type,
                        encoding=Encoding.UTF8,
                        type=PictureType.COVER_FRONT
                    )
                )
                metadata.save()
            elif type(metadata) == MP4 and not metadata.tags.get('covr'):
                logging.info(F"Adding image tag to MP4")
                imageformat = MP4Cover.FORMAT_PNG if mimetypes.guess_extension(cover_image.type) == '.png' else MP4Cover.FORMAT_JPEG
                metadata['covr'] = [ MP4Cover(cover_image.data, imageformat=imageformat)]
                metadata.save()
            elif type(metadata) not in [MP3, MP4] :
                raise TypeError(F"Unkown type {type(metadata)} tagging {str(self)}")
            else :
                logging.info(F"{podcast_file} already has an image")

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

class Image:
    def __init__(self, data, type):
        self.data = data
        self.type = type
