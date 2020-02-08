# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest


class DaftSpider(scrapy.Spider):
    name = 'daft'
    allowed_domains = ['daft.ie']
    start_urls = [
        'https://www.daft.ie/ireland/commercial-property/?ad_type=commercial&advanced=1&searchSource=commercial']

    def start_requests(self):
        yield SplashRequest(
            self.start_urls[0],
            callback=self.scrap_search_result_page,
            args={
                'wait': 1})

    def scrap_search_result_page(self, response):
        links = response.xpath('//div[@class="box"]//span[@class="sr_counter"]/following-sibling::a/@href').extract()
        print(len(links))
        for link in links:
            yield SplashRequest(
                'https://www.daft.ie' + link,  # It is a relative url so we will concat them
                callback=self.parse,  # Set the callback to parse as this will parse the specific commerial let
                args={
                    'wait': 0.5}) # give splash time to render can be lowered

    def parse(self, response):
        print(response.url)
        #original xPaths - classes do not correspond to the divs in webpage - all works except for 'location'
        rent_price = response.xpath('//div[@id="smi-price-string"]//text()').get()
        location = response.xpath('//div[@id="search_result_title_box"]//h2/a/text()').get() #does not work
        size = response.xpath('//div[@id="address_box"]//span[contains(text(),"feet")]//text()').get()
        #still works better than my updated xpath. not sure what the issue is.
        
        #testing new xpaths - matching div tags >> not currently outputting anything
        #rent_price = response.xpath('//div[@class="text-block"]/div/strong[@class="price"]/text()').get()
        #location = response.xpath('//div[@class="search_result_title_box"]/h2/a/text()').get()
        #size = response.xpath('//div[@class="info-box"]/ul/li[2]').get() #done babe

        #only xpath not changes (still returns approapiately)        
        how_many_times_views = response.xpath(
            '//div[@class="description_extras"]//h3[contains(text(),"Property Views:")]/following-sibling::text()[1]').get()

        yield {
            'rent_price': rent_price,
            'location': location,
            'size': size,
            'how_many_times_views': how_many_times_views
        }