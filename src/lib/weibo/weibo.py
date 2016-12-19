# encoding: utf-8

import jieba
import jieba.analyse
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import json
import os
import csv
import pandas
MIN_WORD_LEN = 2
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def map_filter(name,sentlist):
    lines = list()
    for l in sentlist:
        if name in l:
            lines.append(l)
    return lines

def extract(paragraph,topK=1,min_word_len=10):
    ext = jieba.analyse.extract_tags(paragraph, topK=topK, withWeight=False, allowPOS=())
    if len(ext)==0:
        return {}
    # if len(paragraph)< min_word_len:
    #     return {}
    lines = paragraph.split(u'。')
    # for l in lines:
    #     print l
    for _ in ext:
        d = dict()
        d["name"] = _
        filter_lines = map_filter(_, lines)
        d["count"] = len(filter_lines)
        d["children"] = list()
        d["parents"] = list()
        for l in filter_lines:
            key_words = _
            words_parts = l.split(key_words)
            child = extract(words_parts[0],MIN_WORD_LEN)
            if child:
                d["parents"].append(child)
            child = extract(words_parts[-1],MIN_WORD_LEN)
            if child:
                d["children"].append(child)
            if len(words_parts)>2:
                middle = "".join(words_parts[1:-1])
                peek = jieba.analyse.extract_tags(paragraph, topK=topK, withWeight=False, allowPOS=())
                if peek:
                    if middle.find(peek[0]) > middle.find(_):
                        child = extract(middle,MIN_WORD_LEN)
                        #2016-12-17
                        if child:
                            d["parents"].append(child)
                    else:
                        child = extract(middle,MIN_WORD_LEN)
                        # 2016-12-17
                        if child:
                            d["children"].append(child)
        if len(d["parents"])==0:
            d.pop("parents")        
        if len(d["children"])==0:
            d.pop("children")
        return d
    return {}




# with open('sentenTree.json', 'r') as f:
#     resume = f.read()
#
# d = extract(resume,1,MIN_WORD_LEN)
#
# with open('sentenTreeOutput.json', 'w') as f:
#     f.write(json.dumps(d))

print 30 * '*'
in_folder = r'E:\weibocontent'
out_folder = r'E:\weibocontent2'
def get_calc(name):
    for output_dir, _, output_files in os.walk(out_folder):
        for of in output_files:
            if name in of:
                return True
    return False

for dir, _, files in os.walk(in_folder):
    for f in files:
        file_input = os.path.join(in_folder, f)
        file_output = os.path.join(out_folder, f).replace("txt","json")
        #check
        if get_calc(f.rstrip(".txt")):
            print f,"------------calculated--------------"
            continue
        print 30 * '-'
        names=r"repost	comment	attitude	time	text	retweet_time	retweet_text".split('\t')
        print names
        print file_input
        with open(file_input, 'r') as f:
            df = pandas.read_csv(f,names=names,delimiter='\t',quoting=csv.QUOTE_NONE, encoding='utf-8')
            content = "。".join(map(str,df['text']))

            # print content
        d = extract(content,1,MIN_WORD_LEN)

        with open(file_output, 'w') as f:
            f.write(json.dumps(d).decode('unicode-escape'))


print 'job done'
# for e in ext:
#     print e

# print "------"

# tr4w = TextRank4Keyword()
# tr4w.analyze(text=resume, lower=True, window=2)
# kws = tr4w.get_keywords(1, word_min_len=2)    # ÓÐwordºÍweightÊôÐÔ
# kps = tr4w.get_keyphrases(keywords_num=20, min_occur_num=1)

# for k in kws:
#     print k.word

# print "------"

# for k in kps:
#     print k

# print "------"

# tr4s = TextRank4Sentence()
# tr4s.analyze(text=resume, lower=True, source = 'all_filters')
# for item in tr4s.get_key_sentences(num=20,sentence_min_len=1):
#     print " - " + item.sentence
