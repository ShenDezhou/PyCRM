import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
import redis
import functools
from tutorial.items import TorrentItem
from common import *

class MininovaSpider(CrawlSpider):

    name = 'wenshu'
    allowed_domains = ['wenshu.court.gov.cn']
    # start_urls = []
    # rules = [Rule(LinkExtractor(allow=['/tor/\d+']), 'parse')]

    set_cache(20)
    #get 1-200 from redis server
    @property
    def get_formdata():
        return {
            "Param":"法院层级:最高法院",
            "Index":get_cache,
            "Page":20,
            "Order":"法院层级",
            "Direction":"asc"
            }

    def start_requests(self):
        return [scrapy.FormRequest("http://wenshu.court.gov.cn/List/ListContent",
                                   formdata=self.get_formdata,
                                   callback=self.parse,
                                   meta={'Index':i})]

    def get_now_str():
        return datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

    def parse(self,response):
        l = ItemLoader(item=WenshuItem(), response=response)
        l.add_value('url',response.url)
        l.add_value('time',self.get_now_str())
        l.add_value('wenshus',response.body)
        return l.load_item()

from scrapy.contrib.downloadermiddleware import DownloaderMiddleware

class MyCustomDownloaderMiddleware(DownloaderMiddleware):
    def process_request(request, spider):
        return None

    def process_response(request, response, spider):
        if get_cache() < 200:
            incr_cache()
            yield scrapy.FormRequest("http://wenshu.court.gov.cn/List/ListContent",
                                   formdata=self.get_formdata,
                                   callback=self.parse)
        return response

    def process_exception(request, exception, spider):
        if get_cache() < 200:
            yield scrapy.FormRequest("http://wenshu.court.gov.cn/List/ListContent",
                                       formdata=self.get_formdata,
                                       callback=self.parse)
        return None


