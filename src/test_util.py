#!/usr/bin/env python3

from typing import Tuple
import unittest
from parameterized import parameterized

from util import *

class TestUtil(unittest.TestCase):

    @parameterized.expand([
        ["Standard",
         "Mon, 21 Oct 2019 11:00:00 +0000",
         "2019-10-21-1100",
        ],
        ["Standard",
         "Mon, 21 Oct 2019 11:00:00 GMT",
         "2019-10-21-1100",
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
    ])
    def test_remove_unicode(self, name:str, input: str, expected: str):
        self.assertEqual(remove_unicode(input), expected)

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
