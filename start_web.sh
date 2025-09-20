#!/bin/sh
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 60 app:app