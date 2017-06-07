#!/bin/bash
nohup docker run -v /search/PyCRM/src:/search --net=host -e 80:8890 66d6901b944e /search/index.py --port=8890 2>&1 1>/dev/null &
