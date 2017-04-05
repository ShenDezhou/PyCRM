#! /usr/bin/

BIN=./bin/
TMP=./tmp/
LOG=./log/

DBNETGET_BIN=${BIN}dbnetget
OFFSUM=conf/offsum576
PAGES=${1}pages0
PAGESLOG=${LOG}$(basename $1)pages.log

cat $1 | awk -F'\t' '{gsub("\r", "" , $0);print $1}' | ${DBNETGET_BIN} -df cp -i url -o dd -d csum -l ${OFFSUM} -pf ${PAGES} 1>${PAGESLOG} 2>&1
