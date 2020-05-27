import string
import scrapy
from scrapy import Request


class SyriSpider(scrapy.Spider):
    name = 'syri_ac'
    start_urls = ['http://syri.ac/digimss/sortable?keys=&items_per_page=100']

    def parse(self, response):
        table = response.css('table.views-table')
        ms_name = response.css(".views-field-title a::text").extract()
        ms_lang = response.css(".views-field-field-language::text").extract()
        ms_date = response.css(".views-field-field-ms-approximate-date::text").extract()
        ms_contents = response.css(".views-field-body ul li::text").extract()
        ms_link = response.css(".views-field-field-link-to-digitized-manuscri a").xpath("@href").extract()

        yield {table}


