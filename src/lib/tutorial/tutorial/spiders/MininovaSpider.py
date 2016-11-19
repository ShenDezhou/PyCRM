import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader

from tutorial.items import TorrentItem

class MininovaSpider(CrawlSpider):

    name = 'wenshu'
    allowed_domains = ['wenshu.court.gov.cn']
    # start_urls = []
    # rules = [Rule(LinkExtractor(allow=['/tor/\d+']), 'parse')]
    i = 20
    formdata = {
        "Param":"法院层级:最高法院",
        "Index":i,
        "Page":20,
        "Order":"法院层级",
        "Direction":"asc"
        }
    def start_requests(self):
        return [scrapy.FormRequest("http://wenshu.court.gov.cn/List/ListContent",
                                   formdata=formdata,
                                   callback=self.parse)]

    def parse_torrent(self, response):
        torrent = TorrentItem()
        torrent['url'] = response.url
        torrent['name'] = response.xpath("//h1/text()").extract()
        torrent['description'] = response.xpath("//div[@id='description']").extract()
        torrent['size'] = response.xpath("//div[@id='specifications']/p[2]/text()[2]").extract()
        return torrent

    def get_now_str():
        return datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

    def parse(self,response):
        l = ItemLoader(item=TorrentItem(), response=response)
        l.add_value('url',response.url)
        l.add_value('name',)
        l.add_value('description',"//div[@id='description']")
        l.add_value('size',"//div[@id='specifications']/p[2]/text()[2]")
        return l.load_item()

