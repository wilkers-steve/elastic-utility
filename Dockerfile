FROM alpine:3.7
MAINTAINER Steve Wilkerson (wilkers.steve@gmail.com)

RUN apk add --update \
    python \
    py-pip \
  && rm -rf /var/cache/apk/*

RUN pip install \
    elasticsearch==5.5.3 \
    elasticsearch-dsl==5.4.0

COPY bin/elastic-query.py ./elastic-query.py

ENTRYPOINT ["./elastic-query.py"]
