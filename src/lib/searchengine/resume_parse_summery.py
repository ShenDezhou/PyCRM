# encoding: utf-8

import jieba
import jieba.analyse
from textrank4zh import TextRank4Keyword, TextRank4Sentence

with open('resume.txt', 'r') as f:
    resume = f.read()

ext = jieba.analyse.extract_tags(resume, topK=20, withWeight=False, allowPOS=())

for e in ext:
    print e

print "------"

tr4w = TextRank4Keyword()
tr4w.analyze(text=resume, lower=True, window=2)
kws = tr4w.get_keywords(20, word_min_len=2)    # 有word和weight属性
kps = tr4w.get_keyphrases(keywords_num=20, min_occur_num=1)

for k in kws:
    print k.word

print "------"

for k in kps:
    print k

print "------"

tr4s = TextRank4Sentence()
tr4s.analyze(text=resume, lower=True, source = 'all_filters')
for item in tr4s.get_key_sentences(num=3):
    print " - " + item.sentence
