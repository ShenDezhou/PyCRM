#! /usr/bin/python

import zlib
import sys, re

UC="utf8"
GC="gb18030"


def getBlock(file_name, url_dict = None):
	"""Parse the page file
	Return [url, html_string]
	"""
	lineArr = []
	fp=open(file_name,"rb")
	bl = 0 
	url = ""  
	size = 0 
	while True:
		line = fp.readline()
		if len(line) == 0:
			break
		if line.startswith("Error-Reason"):
			fp.readline()
			continue
		if line.startswith("http:"):
			url = line.strip()
			continue
		if line.startswith("Store-Size:"):
			size = int(line.split(":")[1].strip())
			continue
		if len(line.strip()) == 0:
			bl +=1 
		if bl == 2:
			bl = 0 
			htmlstr = ""
			if url_dict != None and url in url_dict:
				fp.seek(size, 1)
				fp.readline()
				continue
			else:
				compresseddata = fp.read(size)
				try:
					htmlstr = zlib.decompress(compresseddata)
				except Exception, e:
					sys.stderr.write("Error: " + url + "\n" + str(e) + "\n")
			
			fp.readline()
			yield [url, htmlstr]  


def test():
	input_file = sys.argv[1]
	for block in getBlock(input_file):
		url = block[0]
		page = block[1] 
		print url
		print page
#		print page.decode(UC).encode(GC)

test()
