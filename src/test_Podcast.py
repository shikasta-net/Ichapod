#!/usr/bin/env python3

from typing import List
import unittest
from parameterized import parameterized

from Podcast import Podcast

class TestPodcast(unittest.TestCase):

    @parameterized.expand([
        ["Two part",
         "Author---http://url.url.co.url/someplace/here.rss",
         ["Author", "http://url.url.co.url/someplace/here.rss"],
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
        ["Two part",
         "Author---http://url.url.co.url/someplace/here.rss",
         ["Author", None, "http://url.url.co.url/someplace/here.rss"],
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
    def test_create(self, name: str, input: str, expected: List[str]):
        result = Podcast.create(input)
        if expected :
            self.assertEqual(result.author, expected[0])
            self.assertEqual(result.series, expected[1])
            self.assertEqual(result.url, expected[2])
        else :
            self.assertEqual(result, expected)
