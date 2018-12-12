FROM alpine:3.7
LABEL maintainer="Steve Wilkerson (wilkers.steve@gmail.com)"

ARG ES_VERSION=5.5.3
ARG ES_DSL_VERSION=5.4.0

RUN apk add --update \
    python \
    py-pip \
  && rm -rf /var/cache/apk/*

RUN pip install \
    elasticsearch==${ES_VERSION} \
    elasticsearch-dsl==${ES_DSL_VERSION}

COPY bin/elastic-query.py ./elastic-query.py

ENTRYPOINT ["./elastic-query.py"]
