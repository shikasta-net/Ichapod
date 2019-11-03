#!/usr/bin/env python3

import mimetypes
from pathlib import Path
from typing import Iterator
import yaml

from Podcast import Podcast

config_file = '../settings.yml' # TODO realtive and hardcoded?

def podcast_list(filename: Path) -> Iterator['Podcast']:
    with open(filename, 'r') as podcast_list:
        for entry in podcast_list.readlines():
            podcast = Podcast.create(entry)
            if podcast:
                yield podcast
            continue


if __name__ == "__main__":
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    temp_download_location = Path(config['temp_download_location'])
    temp_download_location.mkdir(exist_ok=True)

    for podcast in podcast_list(Path(config['podcast_list'])):
        for episode in podcast.episodes():
            #if not episode exists
            episode_path = episode.download(temp_download_location)
            print(episode_path)
