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

keywords=['Canteen','Food','Cafeteria', 'Mid-day Meal','Micro Nutrient']

class GovernmentTenderSpider(scrapy.Spider):
    name = 'government_tender'
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
        yield SeleniumRequest(
                url ='https://www.governmenttenders.net',
                wait_time=30,
                callback=self.parse,
                dont_filter=True,
            )

    def parse(self, response):
        driver= response.meta['driver']
        ignored_exceptions=(StaleElementReferenceException,ElementNotInteractableException,TimeoutException)
        for keyword in keywords:
            driver.get('https://www.governmenttenders.net/advancesearch.aspx')
            country=WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)\
                                        .until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="ctl00_ContentPlaceHolder1_drpCountry"]/option[@value="India"]')))
            country.click()
            sleep(2)
            inputbox=WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)\
                                        .until(EC.presence_of_element_located((By.XPATH, f'//*[@id="ctl00_ContentPlaceHolder1_txtWordSearch"]')))
            inputbox.send_keys(keyword)
            submit=WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)\
                                        .until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="ctl00_ContentPlaceHolder1_btnsubmit"]')))
            submit.click()
            WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)\
                                        .until(EC.presence_of_element_located((By.XPATH, f'//div')))
            previous_identifier=''
            while True:
                html=driver.page_source
                response=Selector(text=html)
                tenderurls=response.xpath('//*[contains(@id,"_imgBuyTender")]/@href').extract()
                for url in tenderurls:
                    tenderurl='https://www.governmenttenders.net/'+url
                    yield Request(url=tenderurl, callback=self.parse_tender)

                nextpage=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_Nextbutton"]/text()').extract_first()
                identifier=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_dgfreshTender_ctl02_pageNO"]/text()').extract_first()
                if identifier!=previous_identifier:                    
                    nextbtn=WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)\
                                                .until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="ctl00_ContentPlaceHolder1_Nextbutton"]')))
                    nextbtn.click()
                    previous_identifier=identifier
                else:
                    break

    def parse_tender(self, response):
        ref_no=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblrefNo"]/text()').extract_first()
        prod_det=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblproductdetailval"]/text()').extract_first()
        tender_location=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lbllocationVal"]/text()').extract_first()
        closing=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblclosingdateval"]/text()').extract_first()
        opening=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblopeningDate"]/text()').extract_first()
        industry=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblSubIndustry"]/text()').extract_first()
        tender_value=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lbltendervalueval"]/text()').extract_first()
        tender_fees=response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lbldocFees"]/text()').extract_first()

        yield {
            'Ref. No':ref_no,
            'Product Details':prod_det,
            'Tender Location':tender_location,
            'Industry':industry,
            'Closing Date':closing,
            'Opening Date':opening,
            'Tender Value':tender_value,
            'Tender Fees':tender_fees

        }
