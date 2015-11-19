# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
from scrapy.http import Request  
#from twisted.enterprise import adbapi
#import MySQLdb.cursors

#from pynlpir import nlpir
#from TextRank4Keyword import TextRank4Keyword
#from TextRank4Sentence import TextRank4Sentence
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import os

class TutorialPipeline(object):
    
    def __init__(self):
        #if(nlpir.Init(nlpir.PACKAGE_DIR,nlpir.UTF8_CODE,None)):
        #    print "\n\ninit success\n\n"
        #else:
        #    print "\n\ninit fail\n\n"
        #print nlpir.SetPOSmap(nlpir.ICT_POS_MAP_FIRST)
        #print os.getcwd()
        self.tr4w = TextRank4Keyword.TextRank4Keyword(stop_words_file='/home/emma/Desktop/Scrapy/tutorial/tutorial//stopword.txt')  
        self.tr4s = TextRank4Sentence.TextRank4Sentence(stop_words_file='/home/emma/Desktop/Scrapy/tutorial/tutorial//stopword.txt')
        #print "success"

        self.file = codecs.open('data.json', mode='wb', encoding='utf-8')
        #self.file = codecs.open('tencent_data.json', mode='wb', encoding='utf-8')
        #self.file = codecs.open('wangyi_data.json', mode='wb', encoding='utf-8')
        #self.file = codecs.open('sina_data.json', mode='wb', encoding='utf-8')
        #self.dbpool = adbapi.ConnectionPool('MySQLdb',host = '52.11.198.252', db='news',user='news', passwd='111111', cursorclass=MySQLdb.cursors.DictCursor,
        #        charset='utf8', use_unicode=False)

        pass

    def process_item(self, item, spider):
        desc = ''
        for s in item['desc']:
            desc+=s
        desc = json.dumps(desc).decode("unicode_escape")
        self.tr4w.train(text=desc, speech_tag_filter=True, lower=True, window=2)
        item['keywords'] = '/'.join(self.tr4w.get_keywords(5, word_min_len=1)) 
        #item['topic'] = '/'.join(self.tr4w.get_keyphrases(keywords_num=1, min_occur_num= 2))  
        self.tr4s.train(text=desc, speech_tag_filter=True, lower=True, source = 'all_filters')
        item['desc'] = '.'.join(self.tr4s.get_key_sentences(num=5)) 

        #query = self.dbpool.runInteraction(self._conditional_insert, item)  
        #query.addErrback(self.handle_error)
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        #return item

    def _conditional_insert(self, tx, item):
        #tx.execute("select * from websites where link = %s", (item['link'][0], ))
        #result = tx.fetchone()
        #if result:
        #    log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        #else:
        if ('author' in item)==False:
            item['author']=[" "]
        tx.execute("insert into News (newsClass, newsTitle, newsFromId, newPlatform, newsContent, newsUrl, newsTime,  newsArea, newsAuthor) values ( %s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['category'][0].encode('utf-8'),item['title'].encode('utf-8'),item['tid'][0].encode('utf-8'),item['platform'][0].encode('utf-8'),item['desc'][0].encode('utf-8'),item['url'][0].encode('utf-8'),item['time'][0].encode('utf-8'),item['newspaper'][0].encode('utf-8'),item['author'][0].encode('utf-8'))
        )
        #tx.execute("");
        print "\n\n\n Item stored in db:"+ item
  
    def handle_error(self, e):
        print "\n\n\n"
        print e 
        print "\n\n\n"

