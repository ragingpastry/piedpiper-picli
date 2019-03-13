FROM python:3.6-alpine

COPY picli /app/picli/
COPY setup.cfg /app/setup.cfg
COPY setup.py /app/setup.py
COPY requirements.txt /app/requirements.txt
COPY tests/functional /app/tests/

WORKDIR /app
RUN pip install -r requirements.txt
RUN python setup.py build
RUN python setup.py install