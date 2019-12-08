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
        ["fail well",
         u"\u00F7",
         None
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

    @parameterized.expand([
        ["Prefix bob left",
         (['adam', 'bob', 'bob', 'bob', 'bobby', 'bobert', 'chris'], string_prefix_comparator_left('bob')),
         1,
        ],
        ["Prefix bob right",
         (['adam', 'bob', 'bob', 'bob', 'bobby', 'bobert', 'chris'], string_prefix_comparator_right('bob')),
         6,
        ],
        ["Prefix bobby right",
         (['adam', 'bob', 'bob', 'bob', 'bobby', 'bobert', 'chris'], string_prefix_comparator_right('bobby')),
         5,
        ],
        ["Prefix james left",
         (['adam', 'bob', 'bob', 'bob', 'bobby', 'bobert', 'chris'], string_prefix_comparator_left('james')),
         7,
        ],
        ["Simple date left",
         (['2019-12-05-0118','2019-12-05-0500','2019-12-05-0900','2019-12-05-1000','2019-12-05-1200','2019-12-05-1745','2019-12-05-1746','2019-12-05-2325','2019-12-06-0010','2019-12-06-1320'], string_prefix_comparator_left('2019-12-05-1520')),
         5,
        ],
        ["Compound prefix date left",
         (['BBC	Home Front	2016-09-27-1115 17	27 September 1916: Juliet Cavendish	urn:bbc:podcast:b07kt27l	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p0443j5w.mp3','BBC	Home Front	2016-09-28-1115 18	28 September 1916: Ivy Layton	urn:bbc:podcast:b07kt27t	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p0443jsp.mp3','BBC	Home Front	2016-09-29-1115 19	29 September 1916: Isabel Graham	urn:bbc:podcast:b07kt289	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p0443kxp.mp3','BBC	Home Front	2016-09-30-1115 20	30 September 1916: Kitty Lumley urn:bbc:podcast:b07kt28n	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p0443lqp.mp3','BBC	Home Front	2016-12-12-1215 21	12 December 1916: Geoffrey Marshall (Season 9 start)	urn:bbc:podcast:b083l9p5	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04g8rtc.mp3','BBC	Home Front	2016-12-13-1215 22	13 December 1916: Marion Wardle urn:bbc:podcast:b083lb2k	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04g8thx.mp3','BBC	Home Front	2016-12-14-1215 23	14 December 1916: Lester Reed	urn:bbc:podcast:b083lbby	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04g8ygw.mp3','BBC	Home Front	2016-12-15-1215 24	15 December 1916: Martha Lamb	urn:bbc:podcast:b083lbc3	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04g91j0.mp3','BBC	Home Front	2016-12-16-1215 25	16 December 1916: Edgar Bates	urn:bbc:podcast:b083lbj0	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04g93v1.mp3','BBC	Home Front	2016-12-19-1215 26	19 December 1916: Alan Lowther	urn:bbc:podcast:b083lbz6	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04g99bc.mp3','BBC	Home Front	2016-12-20-1215 27	20 December 1916: Adeline Lumley	urn:bbc:podcast:b083lbzc	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04gbd4f.mp3','BBC	Home Front	2016-12-21-1215 28	21 December 1916: Marion Wardle urn:bbc:podcast:b083lbzk	.mp3	http://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/http/vpid/p04gb7rg.mp3'], string_prefix_comparator_left('BBC	Home Front	2016-09-30-1115')),
         3,
        ],
    ])
    def test_bisect(self, name: str, input: Tuple, expected: int):
        self.assertEqual(GenericBisect.bisect(*input), expected)
