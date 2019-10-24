
import mimetypes
from datetime import datetime
from pathlib import Path

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
        if not episode['enclosure']['@url']:
            return None

        return cls(
            url = episode['enclosure']['@url'],
            number = episode_number,
            title = episode['title'],
            author = author,
            album = album,
            date = cls._convert_date(episode['pubDate']),
            type = mimetypes.guess_extension(episode['enclosure']['@type']),
            guid = episode['guid']
        )

    def download(self, base_path: Path) -> Path:
        podcast_file = base_path / str(self)
        podcast_file.touch()
        return podcast_file

    @staticmethod
    def _convert_date(date: str) -> datetime:
        input = "%a, %d %b %Y %H:%M:%S %z"
        output = "%Y-%m-%d-%H%M"
        return datetime.strptime(date, input).strftime(output)

    def _filename(self) -> str:
        name = F"{self.date} - {self.title} - {self.author} - {self.album}{self.type}" \
        .replace(u'\u2013', '-') \
        .replace(u'\u2014', '-') \
        .replace(u'\u2018', '\'') \
        .replace(u'\u2019', '\'') \
        .replace(u'\u201c', '\"') \
        .replace(u'\u201d', '\"')

        #check that the character cleanup worked
        name.encode('ascii', 'strict')

        return name

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
