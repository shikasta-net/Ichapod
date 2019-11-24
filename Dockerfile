FROM python:3.6

MAINTAINER Kym Eden

RUN apt-get update && apt-get install -y ffmpeg

ADD requirements.txt log.conf /opt/ichapod/
RUN pip3 install -r /opt/ichapod/requirements.txt

ADD src /opt/ichapod/src
ADD podcasts.txt /var/lib/ichapod/podcasts.txt

VOLUME /podcasts

RUN groupadd --gid 10000 media && useradd --no-log-init -r -g media ichapod

USER ichapod

ENTRYPOINT ["/opt/ichapod/src/Ichapod.py"]
CMD ["--quiet", "--log-config /opt/ichapod/log.config", "/var/lib/ichapod/podcasts.txt", "/podcasts"]
