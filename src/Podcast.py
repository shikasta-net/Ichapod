
from typing import List

class Podcast:
    url: str
    author: str
    series: str

    def __init__(self, url: str, author: str, series: str = None):
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
        return input.split("---")
