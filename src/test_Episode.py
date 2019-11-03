#!/usr/bin/env python3

import logging
from typing import Tuple
import unittest
from parameterized import parameterized

from Episode import Episode

logging.basicConfig(level=logging.FATAL)

class TestPodcast(unittest.TestCase):

    @parameterized.expand([
        ["no URL",
         ("1", "author", "album", dict(enclosure={'@url':""})),
         None,
        ],
        ["example A m4a",
         ("13", "author", "album", dict(title='title',
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij', enclosure={'@url':"http://yes.no.co.uk/file.m4a", '@type':"audio/mp4"})),
         Episode("http://yes.no.co.uk/file.m4a", "13", "title", "author", "album", "2019-10-21-1100", ".m4a", "slkdfjinveosij"),
        ],
        ["example B mp4",
         ("13", u"author\u2019s", u"\u201calbum\u201d", dict(title=u"ti\u2013tle",
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij', enclosure={'@url':"http://yes.no.co.uk/file.mp4", '@type':"audio/mp4"})),
         Episode("http://yes.no.co.uk/file.mp4", "13", "ti-tle", "author's", "\"album\"", "2019-10-21-1100", ".m4a", "slkdfjinveosij"),
        ],
        ["example B mp3",
         ("13", u"author\u2019s", u"\u201calbum\u201d", dict(title=u"ti\u2013tle",
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij', enclosure={'@url':"http://yes.no.co.uk/file.mp3", '@type':"audio/mpeg"})),
         Episode("http://yes.no.co.uk/file.mp3", "13", "ti-tle", "author's", "\"album\"", "2019-10-21-1100", ".mp3", "slkdfjinveosij"),
        ],
        ["Error",
         ("13", u"author\u2019s", u"\u201calbum\u201d", dict(title=u"ti\u2013tle",
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij',)),
         None,
        ],
    ])
    def test_create(self, name: str, input: Tuple[str, str, dict], expected: 'Episode'):
        result = Episode.create(*input)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ["Easy m4a",
         ("audio/mp4", "anything.m4a"),
         ".m4a",
        ],
        ["Harder m4a",
         ("audio/mp4", "anything.mp4"),
         ".m4a",
        ],
        ["Easy mp3",
         ("audio/mp3", "anything.mp3"),
         ".mp3",
        ],
        ["Conflicting mp2-mp3",
         ("audio/mpeg", "a_file.mp3"),
         ".mp3",
        ],
        ["No idea mp2",
         ("audio/mpeg", "a_file"),
         ".mp2",
        ],
        ["What is m4a",
         ("audio/x-m4a", "a_file"),
         ".m4a",
        ],
    ])
    def test_guess_extension(self, name:str, input: Tuple[str, str], expected: str):
        self.assertEqual(Episode._guess_extension(*input), expected)

    @parameterized.expand([
        ["Standard",
         Episode("http://yes.no.co.uk/file.mp3", "13", "title", "author's", "album", "2019-10-21-1100", ".mp4", "slkdfjinveosij"),
         "2019-10-21-1100 - title - author's - album.mp4",
        ],
    ])
    def test_filename(self, name:str, input: Episode, expected: str):
        self.assertEqual(Episode._filename(input), expected)
