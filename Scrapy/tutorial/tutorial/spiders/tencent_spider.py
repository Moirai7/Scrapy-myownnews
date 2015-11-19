
import scrapy
from tutorial.items import TencentItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
import json
import codecs
class TencentSpider(CrawlSpider):
    #filename = codecs.open('tencent_data.json', mode='wb', encoding='utf-8')
    name = "tencent"
    allowed_domains = ["news.qq.com"]
    #start_urls = [
    #    "http://news.qq.com/","http://city.qq.com/","http://gongyi.qq.com/","http://cul.qq.com/","http://mil.qq.com/mil_index.htm","http://news.qq.com/society_index.shtml","http://news.qq.com/world_index.shtml","http://news.qq.com/china_index.shtml"
    #]
    start_urls =["http://news.qq.com/"]

    rules=(
            Rule(LinkExtractor(allow=(r"/a/20\d",)),callback="parse_item",follow=True),

            Rule(LinkExtractor(allow=r"",deny=('m\.','/iask/','/z/','weibo','snapshot','cn/c/2','cn/w/1','/world/99','hi','richtalk','question','auto','baoxian','opinion','roll','club','comment','wp','survey','slide','tag','blog','video','house','bbs','club','app','photo','game','live','vip',)),follow=True),
    )
    def getTitle(self,sel,item):
        title=sel.xpath("/html/head/title/text()").extract()
        if title:
            # print 'title:'+title[0][:-5].encode('utf-8')
            item['title']=title[0]

    def getCate(self,selc,item):
        title = selc.xpath('//span[@class="color-a-0"]/a/text()').extract()
        if(title):
            item['category']=title
        else:
            item['category']=u''
            #item['category'] = title[0].encode('utf-8')
    def getNews(self,selc,item):
        title = selc.xpath('//span[@class="color-a-1"]/a/text()').extract()
        if(title):
            item['newspaper']=title
        else:
            item['newspaper']=u''
            #item['newspaper'] = title[0].encode('utf-8')
    def getAuthor(self,selc,item):
        title = selc.xpath('//span[@class="color-a-3"]/a/text()').extract()
        print title
        if(title):
            item['author']=title
        else:
            item['author']=u'' 
            #item['author'] = title[0].encode('utf-8')
    def getTime(self,selc,item):
        title  = selc.xpath('//span[@class="article-time"]/text()').extract()
        if(title):
            item['time']=title
        else:
            item['time']=u'' 
            #item['time'] = title[0].encode('utf-8')
    def getDesc(self,sel,item):
        title  = sel.xpath('//div[@class="bd"]/div[@id="Cnt-Main-Article-QQ"]/p/text()').extract()
        if(title):
            item['desc'] = title
            #for t in title:
            #    item['desc'] = item['desc']+" "+t.encode('utf-8')

    def parse_item(self, response):      
        item = TencentItem()
        item['platform'] = "tencent"
        item['tid']=response.url.strip().split('/')[-1][:-4]
        self.getTitle(response,item)
        item['url'] = response.url
        self.getCate(response,item)
        self.getNews(response,item)
        self.getAuthor(response,item)
        self.getTime(response,item)
        self.getDesc(response,item)
        if 'desc' in item:
            #line = json.dumps(dict(item)) + '\n'
            #self.filename.write(line.decode("unicode_escape"))
            return item
