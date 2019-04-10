# This is a multi-stage build which requires Docker 17.05 or higher
FROM python:3.7-alpine as picli-builder

WORKDIR /usr/src/picli

ENV PACKAGES="\
	musl-dev \
	git \
    "
RUN apk add --update --no-cache ${PACKAGES}


ADD . .
RUN \
    pip wheel \
    -w dist .

# ✄---------------------------------------------------------------------
# This is an actual target container:

FROM python:3.7-alpine
LABEL maintainer "DREAM <dream@globalinfotek.com>"

ENV PIP_INSTALL_ARGS="\
    --only-binary :all: \
    --no-index \
    -f /usr/src/picli/dist \
    "

COPY --from=picli-builder \
    /usr/src/picli/dist \
    /usr/src/picli/dist

RUN \
    pip install ${PIP_INSTALL_ARGS} "picli" && \
    apk del --no-cache ${BUILD_DEPS} && \
    rm -rf /root/.cache

ENV SHELL /bin/bash
