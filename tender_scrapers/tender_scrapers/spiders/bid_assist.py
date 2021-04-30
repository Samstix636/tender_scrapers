import scrapy
from scrapy import Request


class BidAssistSpider(scrapy.Spider):
    name = 'bid_assist'
    # allowed_domains = ['www.google.com']
    custom_settings={
                'DOWNLOAD_DELAY':'2',
                # 'LOG_LEVEL':'INFO',
                }
    start_urls = ['https://bidassist.com/all-tenders/active?keywords=food%2Ccanteen&filter=KEYWORD:cafeteria%7Cfood%7Ccanteen%7Cmicronutrient%7Cmid-day%20meal&sort=RELEVANCE:DESC&pageNumber=0&pageSize=10&tenderType=ACTIVE&tenderEntity=TENDER_LISTING']

    def parse(self, response):
        yield Request(url='https://bidassist.com/all-tenders/active?keywords=food%2Ccanteen&filter=KEYWORD:cafeteria%7Cfood%7Ccanteen%7Cmicronutrient%7Cmid-day%20meal&sort=RELEVANCE:DESC&pageNumber=0&pageSize=10&tenderType=ACTIVE&tenderEntity=TENDER_LISTING',callback=self.parse_search)

    def parse_search(self, response):
        # tender_url=response.xpath("//a[@class='anchor-wrap']/@href").extract()
        tenders=response.xpath("//div[@class='block card clearfix']")
        for tender in tenders:
            yield{
                'Tender Title':tender.xpath(".//h2[@class='title m-r-5']/a/text()").extract_first(),
                'Description':tender.xpath(".//a[@class='anchor-wrap']/@title").extract_first(),
                'Location':tender.xpath(".//p[@class='location fs-12']/span/text()").extract_first(),
                'Opening Date':tender.xpath(".//h3[text()='Opening Date']/following-sibling::span/text()").extract_first(),
                'Closing Date':tender.xpath(".//h3[text()='Closing Date']/following-sibling::span/text()").extract_first(),
                'Tender Amount':tender.xpath(".//h3[text()='Tender Amount']/following-sibling::span/span/text()").extract_first(),
                'Tender Link':tender.xpath(".//a[@class='anchor-wrap']/@href").extract_first()
                }

        next_url=response.xpath("//li[@class='next']/a/@href").extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse_search)
        
    # def parse_tender(self, response):
    #   yield{
    #       '':response.xpath("").extract_first(),
    #       '':response.xpath("").extract_first(),
    #       '':response.xpath("").extract_first(),
    #       '':response.xpath("").extract_first(),
    #       '':response.xpath("").extract_first(),
    #       '':response.xpath("").extract_first(),
    #   }
        
