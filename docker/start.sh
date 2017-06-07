#!/bin/bash
docker run -v /search/PyCRM/src:/search --net=host -e 80:80 66d6901b944e /search/index.py --port=80
