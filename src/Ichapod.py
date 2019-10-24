#!/usr/bin/env python3

from typing import Iterator
import yaml

from Podcast import Podcast

config_file = '../settings.yml' # TODO realtive and hardcoded?

def podcast_list(filename: str) -> Iterator['Podcast']:
    with open(filename, 'r') as podcast_list:
        for entry in podcast_list.readlines():
            podcast = Podcast.create(entry)
            if podcast:
                yield podcast
            continue


if __name__ == "__main__":
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    for podcast in podcast_list(config['podcast_list']):
        for episode in podcast.episodes():
            print(episode)
