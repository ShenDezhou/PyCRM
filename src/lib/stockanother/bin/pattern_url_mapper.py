#!/bin/env python

import re
import sys

def read_pattern_conf(inputfile):
    patterns = []
    ifile = open(inputfile, "r")
    for line in ifile:
        strs = line.strip().split("\t")
        if len(strs) > 0 and len(strs[0]) > 0:
            patterns.append(re.compile(strs[0]))
    ifile.close()
    return patterns

patterns = read_pattern_conf("pattern.conf")

for line in sys.stdin:
    strs = line.strip().split("\t")
    if len(strs) <= 0:
        continue
    for pattern in patterns:
        if pattern.match(strs[0]) != None:
            print strs[0]
            break
