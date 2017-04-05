#!/bin/sh
ps -ef | grep $1 | kill -9 `awk '{print $2}'`
