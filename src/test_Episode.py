#!/usr/bin/env python3

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
        ["example A",
         ("13", "author", "album", dict(title='title',
         pubDate='Mon, 21 Oct 2019 11:00:00 +0000', guid='slkdfjinveosij', enclosure={'@url':"http://yes.no.co.uk/file.mp3", '@type':"audio/mp4"})),
         Episode("http://yes.no.co.uk/file.mp3", "13", "title", "author", "album", "Mon, 21 Oct 2019 11:00:00 +0000", "audio/mp4", "slkdfjinveosij"),
        ],
    ])
    def test_create(self, name: str, input: Tuple[str, str, dict], expected: 'Episode'):
        result = Episode.create(*input)
        self.assertEqual(result, expected)
