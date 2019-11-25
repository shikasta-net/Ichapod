#!/usr/bin/env python3

import argparse
import datetime
import logging, logging.config
import mimetypes
from pathlib import Path
from typing import Iterator

from Episode import Episode
from Podcast import Podcast

parser = argparse.ArgumentParser(description='Download podcasts.')
parser.add_argument('podcast_list', type=Path, help='Podcast list')
parser.add_argument('destination_folder', type=Path, help='Where podcasts are saved')
parser.add_argument('--temp_download_location', type=Path, default='/tmp/downloaded_episode', help='Where podcasts are saved')
parser.add_argument('--log-config', type=Path, default='../log.conf', help='Logging config file name')
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

def move(downloaded_file: Path, podcast_file: Path, over_write=False) -> bool :
    podcast_file.parent.mkdir(parents=True, exist_ok=True)
    if over_write and podcast_file.exists() :
        logging.warning(F"Force replacing {podcast_file}")
        podcast_file.unlink()
    if podcast_file.exists():
        logging.error(F"{podcast_file} already exists")
        return False
    try:
        with podcast_file.open(mode='xb') as output:
            output.write(downloaded_file.read_bytes())
            downloaded_file.unlink()
        return True
    except:
        logging.error(F"Unable to copy {downloaded_file} to {podcast_file}")
        set_error(1)
        return False


if __name__ == "__main__":

    actual_run = not args.dry_run

    logging.getLogger().setLevel(logging.INFO)
    logging.info(F"Starting update {datetime.datetime.now().replace(microsecond=0)}\n{'-'*43}")
    if not actual_run :
        logging.info("Performing dry-run")
    logging.info("Updating podcasts from list")
    if args.over_write :
        logging.warning("OVERWRITE IS ENABLED")
    logging.getLogger().setLevel(log_level)

    temp_download_location = args.temp_download_location
    temp_download_location.mkdir(parents=True, exist_ok=True)

    podcast_store_location = args.destination_folder

    for podcast in podcast_list(args.podcast_list):
        for episode in podcast.episodes():
            #skip already downloaded
            podcast_file = podcast_store_location / str(podcast) / str(episode)
            if podcast_file.exists() and episode == Episode.load(podcast_file):
                logging.info(F"Skipping already downloaded {episode}")
                continue
            #if not episode exists
            downloaded_file = episode.download_to(temp_download_location)
            if actual_run and downloaded_file and move(downloaded_file, podcast_file, args.over_write):
                logging.info(F"Fetch completed for {podcast_file.relative_to(podcast_store_location)}")
                #store result to avoid repetition
            elif downloaded_file:
                downloaded_file.unlink()
                logging.info(F"Dry-run fetch completed for {podcast_file.relative_to(podcast_store_location)}")
            else:
                logging.error(F"Episode {episode} not downloaded")


    logging.getLogger().setLevel(logging.INFO)
    logging.info(F"Done updating\n{'='*43}")
