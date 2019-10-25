#!/usr/bin/env python3

import logging
import mimetypes
from typing import Tuple
import unittest
from parameterized import parameterized

from Episode import Episode

logging.basicConfig(level=logging.FATAL)

class TestPodcast(unittest.TestCase):

    def setUp(self):
        mimetypes.add_type('audio/mp4', '.mp4')

    @parameterized.expand([
        ["no URL",
         ("1", "author", "album", dict(enclosure={'@url':""})),
         None,
        ],
        ["example A",
         ("13", "author", "album", dict(title='title',
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij', enclosure={'@url':"http://yes.no.co.uk/file.mp3", '@type':"audio/mp4"})),
         Episode("http://yes.no.co.uk/file.mp3", "13", "title", "author", "album", "2019-10-21-1100", ".mp4", "slkdfjinveosij"),
        ],
        ["example B",
         ("13", u"author\u2019s", u"\u201calbum\u201d", dict(title=u"ti\u2013tle",
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij', enclosure={'@url':"http://yes.no.co.uk/file.mp3", '@type':"audio/mp4"})),
         Episode("http://yes.no.co.uk/file.mp3", "13", "ti-tle", "author's", "\"album\"", "2019-10-21-1100", ".mp4", "slkdfjinveosij"),
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
        ["Standard",
         Episode("http://yes.no.co.uk/file.mp3", "13", "title", "author's", "album", "2019-10-21-1100", ".mp4", "slkdfjinveosij"),
         "2019-10-21-1100 - title - author's - album.mp4",
        ],
    ])
    def test_filename(self, name:str, input: Episode, expected: str):
        self.assertEqual(Episode._filename(input), expected)
