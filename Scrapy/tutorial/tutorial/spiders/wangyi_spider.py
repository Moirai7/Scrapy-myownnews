import scrapy
from tutorial.items import TencentItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
import json
import codecs
class WangYiSpider(CrawlSpider):
        #filename = codecs.open('wangyi_data.json', mode='wb', encoding='utf-8')
        
        name = "wangyi"
        
        #start_urls = ['http://news.qq.com/','http://news.163.com/','http://news.sina.com.cn/']
        start_urls = ['http://news.163.com/']
        rules=(
            Rule(LinkExtractor(allow=r"/\d+/\d+/\d+/*",allow_domains=('news.163.com')),callback="parse_news",follow=True),

            Rule(LinkExtractor(allow=r"",allow_domains = ("news.163.com"),deny=('m\.','/iask/','/z/','weibo','snapshot','cn/c/2','cn/w/1','/world/99','hi','richtalk','question','auto','baoxian','opinion','roll','club','comment','wp','survey','slide','tag','blog','video','house','bbs','club','app','photo','game','live','vip',)),follow=True),
             
        )
        def parse_news(self,response):
            item = TencentItem()
            item['platform'] = "wangyi"
            item['tid']=response.url.strip().split('/')[-1][:-5]
            # self.get_thread(response,item)
            self.get_title(response,item)
            self.get_source(response,item)
            self.get_url(response,item)
            self.get_news_from(response,item)
            self.get_from_url(response,item)
            self.get_text(response,item)
            if 'desc' in item:
                #line = json.dumps(dict(item)) + '\n'
                item['author']=u''
                return item

        def get_title(self,response,item):
            title=response.xpath("/html/head/title/text()").extract()
            if title:
                # print 'title:'+title[0][:-5].encode('utf-8')
                item['title']=title[0][:-5]
                item['title']=item['title'].strip(' ')

        def get_source(self,response,item):
            source=response.xpath("//div[@class='ep-time-soure cDGray']/text()").extract()
            if source:
                # print 'source'+source[0][:-5].encode('utf-8')
                item['time']=source[0][:-5]
            else:
                item['time']=u''
        def get_news_from(self,response,item):
            news_from=response.xpath("//a[@id='ne_article_source']/text()").extract()
            if news_from:
                # print 'from'+news_from[0].encode('utf-8')     
                item['newspaper']=news_from[0]
            else:
                item['newspaper']=u''
        def get_from_url(self,response,item):
            from_url=response.xpath("//span[@class='ep-crumb JS_NTES_LOG_FE']/a/text()").extract()
            if from_url:
                # print 'url'+from_url[0].encode('utf-8')       
                item['category']=from_url[1]    
            else:
                item['category']=u''
        def  get_text(self,response,item):
            news_body=response.xpath("//div[@id='endText']/p/text()").extract()
            if news_body:
                # for  entry in news_body:
                #   print entry.encode('utf-8')
                item['desc']=news_body 
        def get_url(self,response,item):
            news_url=response.url
            if news_url:
                item['url']=news_url

