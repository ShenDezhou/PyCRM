# Scrapy settings for dirbot project

SPIDER_MODULES = ['dirbot.spiders']
NEWSPIDER_MODULE = 'dirbot.spiders'
DEFAULT_ITEM_CLASS = 'dirbot.items.Website'

ITEM_PIPELINES = {'dirbot.pipelines.FilterWordsPipeline': 1}

FEED_URI = '/root/jupiter/PyCRM/src/lib/dirbot/scrapy.json'
FEED_FORMAT = 'jsonlines'