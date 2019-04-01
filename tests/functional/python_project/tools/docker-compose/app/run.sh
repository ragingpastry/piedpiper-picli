#!/bin/sh
/bin/sh -c "/usr/bin/gunicorn -c /charon/gunicorn.py 'app:create_app()'"