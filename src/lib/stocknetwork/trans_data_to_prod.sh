#! /bin/bash
#coding=gbk
. ./bin/tool.sh

iconv -fgbk -tutf8 data/crumb/xueqiu.url.types  -o data/crumb/xueqiu.url.types.utf8
iconv -fgbk -tutf8 data/crumb/xueqiu.crumb -o data/crumb/xueqiu.crumb.utf8

copy_file data/crumb web xueqiu.url.types.utf8 
copy_file data/crumb web xueqiu.crumb.utf8 