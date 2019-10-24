#!/usr/bin/env python3

from typing import List
import unittest
from parameterized import parameterized

from Podcast import Podcast

class TestPodcast(unittest.TestCase):

    @parameterized.expand([
        ["URL Only",
         "http://url.url.co.url/someplace/here.rss",
         ["http://url.url.co.url/someplace/here.rss"],
        ],
        ["Three part",
         "Author---Series---http://url.url.co.url/someplace/here.rss",
         ["Author", "Series", "http://url.url.co.url/someplace/here.rss"],
        ],
        ["Ignored simple",
         "#Author---Series---http://url.url.co.url/someplace/here.rss",
         None,
        ],
        ["Ignored with spaces",
         "   #Author---Series---http://url.url.co.url/someplace/here.rss",
         None,
        ],
    ])
    def test_tokenise(self, name: str, input: str, expected: List[str]):
        result = Podcast._tokanise(input)
        self.assertEqual(result, expected)


    @parameterized.expand([
        ["URL only",
         "http://url.url.co.url/someplace/here.rss",
         Podcast("http://url.url.co.url/someplace/here.rss"),
        ],
        ["Two part",
         "Author---http://url.url.co.url/someplace/here.rss",
         Podcast("http://url.url.co.url/someplace/here.rss", "Author"),
        ],
        ["Three part",
         "Author---Series---http://url.url.co.url/someplace/here.rss",
         Podcast("http://url.url.co.url/someplace/here.rss", "Author", "Series"),
        ],
        ["Ignored simple",
         "#Author---Series---http://url.url.co.url/someplace/here.rss",
         None,
        ],
        ["Ignored with spaces",
         "   #Author---Series---http://url.url.co.url/someplace/here.rss",
         None,
        ],
    ])
    def test_create(self, name: str, input: str, expected: 'Podcast'):
        result = Podcast.create(input)
        self.assertEqual(result, expected)

    @unittest.skip("Network reliance")
    def test_get_manifest(self):
        url = "http://guiltyfeminist.libsyn.com/rss"

        result = Podcast(url)._get_manifest()
        self.assertIsInstance(result, dict)
        self.assertIsNotNone(result)
