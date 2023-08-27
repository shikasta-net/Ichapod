#!/usr/bin/env python3

from typing import List
import unittest
from parameterized import parameterized

from src.Podcast import Podcast

class TestPodcast(unittest.TestCase):

    @parameterized.expand([
        ["URL only",
         dict(url= "http://url.url.co.url/someplace/here.rss"),
         Podcast("http://url.url.co.url/someplace/here.rss"),
        ],
        ["Two part",
         dict(author="Author", url="http://url.url.co.url/someplace/here.rss"),
         Podcast("http://url.url.co.url/someplace/here.rss", "Author"),
        ],
        ["Three part",
         dict(author="Author", series="Series", url="http://url.url.co.url/someplace/here.rss"),
         Podcast("http://url.url.co.url/someplace/here.rss", "Author", "Series"),
        ],
        ["Ignored simple",
         dict(enabled=False, author="Author", series="Series", url="http://url.url.co.url/someplace/here.rss"),
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
