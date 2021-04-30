import scrapy
from time import sleep
from datetime import datetime
import pandas as pd
import json
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from time import sleep
from scrapy.selector import Selector
from scrapy import Request
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
import random
from shutil import which

tdr_list=[]
search_urls=['https://www.tender247.com/keyword/Food+Tenders#',
                'https://www.tender247.com/keyword/Canteen+Tenders',
                'https://www.tender247.com/keyword/Cafeteria+Tenders',
                'https://www.tender247.com/keyword/Mid-day+meal+Tenders', 
                'https://www.tender247.com/keyword/MicroNutrient+Tenders',
                ]

class Tender247Spider(scrapy.Spider):
    name = 'tender247'
    # allowed_domains = ['www.google.com']
    # start_urls = ['http://www.google.com/']
    custom_settings={
                'DOWNLOAD_DELAY':'3',
                'LOG_LEVEL':'INFO',
                'DOWNLOADER_MIDDLEWARES':{'scrapy_selenium.SeleniumMiddleware': 800},
                'SELENIUM_DRIVER_NAME':'chrome',
                'SELENIUM_DRIVER_EXECUTABLE_PATH' : which('chromedriver'),
                'SELENIUM_DRIVER_ARGUMENTS':['--non headless',"--ignore-certificate-errors","--disable-extensions","--no-sandbox","--disable-dev-shm-usage",'--log-level=3']
 # '--disable-gpu'

                }

    def start_requests(self):
        yield SeleniumRequest(url ='https://www.tender247.com', wait_time=30, callback=self.parse, dont_filter=True )
    def parse(self, response):
        driver= response.meta['driver']
        ignored_exceptions=(StaleElementReferenceException,ElementNotInteractableException,TimeoutException)
        for search_url in search_urls:
            driver.get(search_url)
            SCROLL_PAUSE_TIME = 2

            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            html=driver.page_source
            response=Selector(text=html)
            tenders=response.xpath("//td/div/a/@onclick").extract()
            for tender in tenders:
                url=tender.strip("viewTenderDetails('").replace("');", '')
                tender_url='https://www.tender247.com'+url
                yield Request(url=tender_url, callback=self.parse_tender)

    def parse_tender(self, response):
        ref_no=response.xpath("//td[contains(text(),'T247')]/following-sibling::td/text()").extract_first()
        detail=response.xpath('//*[@id="pReqBrief"]/text()').extract_first()
        est_cost=response.xpath("//td[contains(text(),'Estimated Cost')]/following-sibling::td/span/text()").extract()[-1]
        emd=response.xpath("//td[contains(text(),'EMD')]/following-sibling::td/span/text()").extract()
        closing_date=response.xpath("//td[contains(text(),'Last Date')]/following-sibling::td/text()").extract_first()
        opening_date=response.xpath("//td[contains(text(),'Opening Date')]/following-sibling::td/text()").extract_first()
        location=response.xpath("//td[contains(text(),'Location')]/following-sibling::td/text()").extract_first()
        if ref_no in tdr_list:
            pass
        else:
            tdr_list.append(ref_no)
            yield{
                'Reference No':ref_no,
                'Brief':detail,
                'Estimated Cost':est_cost,
                'EMD':emd,
                'Closing Date':closing_date,
                'Opening Date':opening_date,
                'location':location,
                'Tender Link':response.url
            }
