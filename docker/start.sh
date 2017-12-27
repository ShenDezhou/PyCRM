#!/bin/bash
docker run -d --name crm -v /root/PyCRM/src:/search --net=host bangtech/crm_web /search/index.py --port=8890
