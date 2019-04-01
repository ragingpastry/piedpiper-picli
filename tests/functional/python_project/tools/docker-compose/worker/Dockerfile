FROM alpine

COPY requirements.txt /

RUN apk add --update python py-pip
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    make \
    ca-certificates \
    python-dev \
    openssl-dev \
    libxml2 \
    libxslt-dev \
    libxml2-dev \
    libxslt \
    libxslt-dev \
    libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    mkdir -p /charon/charon

COPY charon /charon/charon/
COPY dist/charon-0.1-py2-none-any.whl /charon
RUN pip install /charon/charon-0.1-py2-none-any.whl && apk add --no-cache libxslt
WORKDIR /charon
CMD ["python", "charon/worker.py"]