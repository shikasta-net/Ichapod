#!/bin/bash
# Ichapod was oringinally a Bash script by Patrick Simonds (divinitycycle@gmail.com) inspired by BashPodder
# Completely reworked in Python by Kym Eden

set -e

docker run --rm -v /tmp/podcasts/podcast-list.yml:/var/lib/ichapod/podcasts.yml:ro -v /tmp/podcasts:/podcasts:rw --user 1000:10000 shikasta/ichapod --log-config=/opt/ichapod/log.conf /var/lib/ichapod/podcasts.yml /podcasts "$@"
