#!/usr/bin/env python3

import argparse
import datetime
import logging, logging.config
import mimetypes
from pathlib import Path
from typing import Iterator
import yaml

from Podcast import Podcast

parser = argparse.ArgumentParser(description='Download podcasts.')
parser.add_argument('--config', default='../settings.yml', help='Config file name')
parser.add_argument('--log-config', default='../log.conf', help='Logging config file name')
parser.add_argument('--dry-run', '-n', action='store_true', help='Don\'t run the real fetcher')
parser.add_argument('--over-write', '-f', action='store_true', help='Replace an existing file if found')
log_arg = parser.add_mutually_exclusive_group()
log_arg.add_argument('--debug', action='store_true', help='Logging to debug')
log_arg.add_argument('--quiet', '-q', action='store_true', help='Logging to quiet')

args = parser.parse_args()

logging.config.fileConfig(args.log_config)

if args.quiet:
    log_level = logging.WARNING
elif args.debug:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

def podcast_list(filename: Path) -> Iterator['Podcast']:
    with open(filename, 'r') as podcast_list:
        for entry in podcast_list.readlines():
            podcast = Podcast.create(entry)
            if podcast:
                yield podcast
            continue


if __name__ == "__main__":
    config_file = args.config
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    actual_run = not args.dry_run

    logging.getLogger().setLevel(logging.INFO)
    logging.info(F"Starting update {datetime.datetime.now().replace(microsecond=0)}\n{'-'*43}")
    if not actual_run :
        logging.info("Performing dry-run")
    logging.info("Updating podcasts from list")
    if args.over_write :
        logging.warning("OVERWRITE IS ENABLED")
    logging.getLogger().setLevel(log_level)

    temp_download_location = Path(config['temp_download_location'])
    temp_download_location.mkdir(parents=True, exist_ok=True)

    for podcast in podcast_list(Path(config['podcast_list'])):
        for episode in podcast.episodes():
            #if not episode exists
            episode_path = episode.download(temp_download_location)
            print(episode_path)

    logging.getLogger().setLevel(logging.INFO)
    logging.info(F"Done updating\n{'='*43}")
