#!/usr/bin/env sh
install_reqs="
    alpine-sdk
    libffi-dev
    openssl-dev
    libxml2-dev
    libxslt-dev
"
apk add ${install_reqs}
pip install -r $(dirname "$0")/../requirements.txt
pytest --ignore=src/molecule --cov=charon