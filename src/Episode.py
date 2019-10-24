
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
            date = episode['pubDate'],
            type = episode['enclosure']['@type'],
            guid = episode['guid']
        )

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
        return self.number < other.number

    def __str__(self):
        return F"{self.number} - {self.title} - {self.author} - {self.album}"
