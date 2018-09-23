FROM ubuntu:14.04

MAINTAINER Kym Eden

RUN apt-get update && \
    apt-get dist-upgrade --yes --no-install-recommends --no-install-suggests && \
    apt-get install --yes --no-install-recommends --no-install-suggests ca-certificates wget xsltproc eyed3 mp3gain && \
    apt-get clean

ADD ichapod.sh /usr/sbin/ichapod
ADD readpodcast.xsl /var/lib/ichapod/readpodcast.xsl
ADD settings /etc/default/ichapod
ADD podcasts.txt /var/lib/ichapod/podcasts.txt

VOLUME /podcasts

ENTRYPOINT ["ichapod"]
CMD []
