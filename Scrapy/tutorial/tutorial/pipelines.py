# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
from scrapy.http import Request  

import os
from hashlib import md5
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

from textrank4zh import TextRank4Keyword, TextRank4Sentence

class JsonWithEncodingCnblogsPipeline(object):
    
    def __init__(self):
        self.file = codecs.open('data.json', mode='wb', encoding='utf-8')

        pass

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        return item

    def spider_closed(self, spider):
        self.file.close()


class MySQLStoreCnblogsPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.tr4w = TextRank4Keyword.TextRank4Keyword(stop_words_file='stopword.txt')
        self.tr4s = TextRank4Sentence.TextRank4Sentence(stop_words_file='stopword.txt')
    
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    #pipeline默认调用
    def process_item(self, item, spider):
        self.tr4w.train(text=u'\u3002'.join(item['desc']),speech_tag_filter=True, lower=True, window=2) 
        sentences = self.tr4s.train(text=u'\u3002'.join(item['desc']), speech_tag_filter=True, lower=True, source = 'all_filters')
        item['keywords']='/'.join(self.tr4w.get_keywords(5, word_min_len=2))
        if 'keywords' not in item:
            item['keywords']=u''
        if len(sentences)>5:
            item['desc']=u'\u3002'.join(self.tr4s.get_key_sentences(num=5))
        else:
            item['desc']=u'\u3002'.join(item['desc'])

        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        #return d

    #将每行更新或写入数据库中
    def _do_upinsert(self, conn, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        conn.execute("""
                select 1 from News where newsMd5 = %s
        """, (linkmd5id, ))
        ret = conn.fetchone()
        if ret:
            pass
        else:
            sql =  """INSERT INTO `News`  (`newsClass`, `newsTitle`, `newPlatform`, `newsContent`, `newsUrl`, `newsTime`,`newsAuthor`, `newsMd5`,`newsKeywords`) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)"""

            conn.execute(sql, (item['category'].encode('utf-8'), item['title'].encode('utf-8'), item['platform'].encode('utf-8'), item['desc'].encode('utf-8'), item['url'].encode('utf-8'), item['time'].encode('utf-8'), item['author'].encode('utf-8'), linkmd5id,item['keywords'].encode('utf-8')))

            print "\n\n"+"saved"+"\n\n"

    #获取url的md5编码
    def _get_linkmd5id(self, item):
        #url进行md5处理，为避免重复采集设计
        return md5(item['url']).hexdigest()
    #异常处理
    def _handle_error(self, failue, item, spider):
        print failure
