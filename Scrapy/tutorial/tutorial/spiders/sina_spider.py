import scrapy
from tutorial.items import TencentItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
import json
import codecs
class SinaSpider(CrawlSpider):
        #filename = codecs.open('sina_data.json', mode='wb', encoding='utf-8')
        name = "sina"
        allowed_domains = ["news.sina.com.cn"]
        #start_urls = ['http://news.sina.com.cn/pl/2015-07-15/073232109330.shtml']
        start_urls = ['http://news.sina.com.cn/']
        rules=(
            Rule(LinkExtractor(allow=(r"/2014\-",r"/2015\-")),callback="parse_news",follow=True),

            Rule(LinkExtractor(allow=r"",deny=('m\.','/iask/','/z/','weibo','snapshot','cn/c/2','cn/w/1','/world/99','hi','richtalk','question','auto','baoxian','opinion','roll','club','comment','wp','survey','slide','tag','blog','video','house','bbs','club','app','photo','game','live','vip',)),follow=True),
        )

        def parse_news(self,response):
            item = TencentItem()
            item['platform'] = "sina"
            item['tid']=response.url.strip().split('/')[-1][:-6]
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

        def get_source(self,response,item):
            source=response.xpath("//span[@class='time-source']/text()").extract()
            if source:
                # print 'source'+source[0][:-5].encode('utf-8')
                item['time']=source[0]
            else:
                source = response.xpath("//span[@id='pub_date']/text()").extract()
                if source:
                    item['time']=source[0]
                else:
                    item['time']=u''

        def get_news_from(self,response,item):
            news_from=response.xpath("//span[@data-sudaclick='media_name']/a/text()").extract()
            if news_from:
                # print 'from'+news_from[0].encode('utf-8')     
                item['newspaper']=news_from[0]
            else:
                news_from = response.xpath("//span[@id='media_name']/a[@data-sudaclick='media_name']/text()").extract()
                if news_from:
                    item['newspaper']=news_from[0]
                else:
                    item['newspaper']=u''

        def get_from_url(self,response,item):
            from_url=response.xpath("//div[@class='site-header clearfix']/div[@class='bread']/a/text()").extract()
            if from_url:
                # print 'url'+from_url[0].encode('utf-8')       
                item['category']=from_url[0]  
            else:
                from_url = response.xpath("//span[@id='blkBreadcrumbLink']/a/text()").extract()
                if from_url:
                    item['category']=from_url[0] 
                else:
                    item['category']=u'' 

        def  get_text(self,response,item):
            news_body=response.xpath("//div[@id='artibody']/p/text()").extract()
            if news_body:
                # for  entry in news_body:
                #   print entry.encode('utf-8')
                item['desc']=news_body 

        def get_url(self,response,item):
            news_url=response.url
            if news_url:
                #print news_url 
                item['url']=news_url
