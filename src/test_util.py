#!/usr/bin/env python3

from typing import Tuple
import unittest
from parameterized import parameterized

from util import *
from util import __ok_unicode as ok_unicode

class TestUtil(unittest.TestCase):

    @parameterized.expand([
        ["Standard",
         "Mon, 20 Oct 2019 11:00:00 +0000",
         "2019-10-20-1100",
        ],
        ["Before midday",
         "Thu, 18 Apr 2019 06:24:00 +0000",
         "2019-04-18-0624",
        ],
        ["Timezone letters GMT",
         "Mon, 21 Oct 2019 11:00:00 GMT",
         "2019-10-21-1100",
        ],
        ["Timezone number plus 4",
         "Mon, 21 Oct 2019 11:00:00 +0400",
         "2019-10-21-1100",
         #"2019-10-21-0700",
        ],
        ["Timezone letters EDT",
         "Wed, 23 Oct 2019 12:00:00 EDT",
         "2019-10-23-1200",
         #"2019-10-23-1600",
        ],
        ["Load from file",
         "2019-10-23 1200",
         "2019-10-23-1200",
         #"2019-10-23-1600",
        ],
        ["Load from file missing start",
         "2019-04-18 624",
         "2019-04-18-0624",
         #"2019-10-23-1600",
        ],
        ["Load from file missing more",
         "2019-04-18 0",
         "2019-04-18-0000",
         #"2019-10-23-1600",
        ],
    ])
    def test_parse_date(self, name:str, input: str, expected: str):
        self.assertEqual(convert_date(input), expected)

    @parameterized.expand([
        ["Standard",
         u"ti\u2013tle",
         "ti-tle",
        ],
        ["Long",
         u"2019-10\u201321-1100 - title - author\u2019s - \u201calbum\u201d",
         "2019-10-21-1100 - title - author's - \"album\"",
        ],
        ["example a",
         u"2011-10-08-1007 - 1950′s Housewives - The History Chicks - The History Chicks.mp3",
         "2011-10-08-1007 - 1950's Housewives - The History Chicks - The History Chicks.mp3"
        ],
        ["example b",
         u"Lisa Randall —\xa0Dark Matter, Dinosaurs, and Extra Dimensions",
         "Lisa Randall - Dark Matter, Dinosaurs, and Extra Dimensions"
        ],
        ["fix whitespace",
         u"Lisa   Randall:\t\tDark Matter,\tDinosaurs   , and Extra Dimensions",
         "Lisa Randall: Dark Matter, Dinosaurs, and Extra Dimensions"
        ],
        ["ignore ok",
         "".join(ok_unicode),
         "".join(ok_unicode)
        ],
    ])
    def test_remove_unicode(self, name:str, input: str, expected: str):
        self.assertEqual(remove_unicode(input), expected)

    @parameterized.expand([
        ["Simple",
         "A generally good title",
         "A generally good title",
        ],
        ["Unicode",
         "the Names \u2013 A generally good title",
         "the Names: A generally good title",
        ],
        ["Wrong punctuation",
         "What is going on here: a better look at things?",
         "What is going on here: a better look at things?",
        ],
        ["Wrong punctuation",
         "What is going on here - a better look at things",
         "What is going on here: a better look at things",
        ],
    ])
    def test_clean_title(self, name:str, input: str, expected: str):
        self.assertEqual(clean_title(input), expected)

    @parameterized.expand([
        ["Simple",
         "file.ext",
         "file.ext",
        ],
        ["Unicode",
         u"2019-10\u201321-1100 - title - author\u2019s - \u201calbum\u201d.mp4",
         "2019-10-21-1100 - title - author's - \"album\".mp4",
        ],
        ["Illeglas",
         "2019-10-21-1100 - title? - authors: a / b , c - album: album,   the.mp4",
         "2019-10-21-1100 - title - authors, a, b, c - album, album, the.mp4",
        ],
    ])
    def test_sanitise_path(self, name:str, input: str, expected: str):
        self.assertEqual(sanitise_path(input), expected)
