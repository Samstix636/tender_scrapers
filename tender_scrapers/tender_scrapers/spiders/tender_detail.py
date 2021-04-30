import scrapy
from scrapy import Request

tdr_list=[]

class TenderDetailSpider(scrapy.Spider):
    name = 'tender_detail'
    # allowed_domains = ['www.google.com']
    start_urls = ['https://www.tenderdetail.com/Indian-Tenders', 'https://www.tenderdetail.com/Indian-tender/food-tenders']

    def parse(self, response):
        tender_row=response.xpath("//div[@class='tender_row']")
        for tender in tender_row:
            title=tender.xpath(".//p/span/text()").extract()[-1]
            if 'food' in title or 'canteen' in title or 'cafeteria' in title or 'mid day meal' in title:
                url=tender.xpath(".//a[@class='viewnotice']/@href").extract_first()
                yield Request(url=url, callback=self.parse_tender)

        next_url=response.xpath("//li[@class='PagedList-skipToNext']/a/@href").extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_tender(self, response):
        tdr_id=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div/text())").extract_first()
        detail=(response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/div[3]/div/text())").extract())[-1]
        competition_type=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/div[4]/div/text())").extract_first()
        state=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/div[5]/div/text())").extract_first()
        closing_date=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/div[7]/div/text())").extract_first()
        opening_date=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/div[8]/div/text())").extract_first()
        doc_fee=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[5]/div[2]/div[1]/div[2]/text())").extract_first()
        tender_value=response.xpath("normalize-space(/html/body/div[1]/div[2]/div/div/div[1]/div[5]/div[2]/div[3]/div[2]/text())").extract_first()
        if tdr_id in tdr_list:
            pass
        else:
            tdr_list.append(tdr_id)
            yield{
                'Tender ID':tdr_id,
                'Tender Brief':detail,
                'Competition Type':competition_type,
                'State':state,
                'Closing Date':closing_date,
                'Opening Date':opening_date,
                'Tender Value':tender_value,
                'Document Fee':doc_fee,
                'Tender Link':response.url
            }
