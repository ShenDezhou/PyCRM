#!/bin/bash
docker rm -f crm1
docker run -d --name crm1 -v /root/PyCRM/src/config_web1.py:/search/config_web.py --net=host bangtech/crm_web:latest /search/index.py --port=18890 
