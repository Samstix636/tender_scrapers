import scrapy


class TendertigerSpider(scrapy.Spider):
    name = 'tendertiger'
    allowed_domains = ['www.google.com']
    start_urls = ['http://www.google.com/']

    def parse(self, response):
        pass
