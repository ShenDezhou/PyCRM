from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader

from tutorial.items import TorrentItem

class MininovaSpider(CrawlSpider):

    name = 'mininova'
    allowed_domains = ['mininova.org']
    start_urls = ['http://www.mininova.org/yesterday']
    rules = [Rule(LinkExtractor(allow=['/tor/\d+']), 'parse')]

    def parse_torrent(self, response):
        torrent = TorrentItem()
        torrent['url'] = response.url
        torrent['name'] = response.xpath("//h1/text()").extract()
        torrent['description'] = response.xpath("//div[@id='description']").extract()
        torrent['size'] = response.xpath("//div[@id='specifications']/p[2]/text()[2]").extract()
        return torrent

    def parse(self,response):
        l = ItemLoader(item=TorrentItem(), response=response)
        l.add_value('url',response.url)
        l.add_xpath('name',"//h1/text()")
        l.add_xpath('description',"//div[@id='description']")
        l.add_xpath('size',"//div[@id='specifications']/p[2]/text()[2]")
        return l.load_item()

