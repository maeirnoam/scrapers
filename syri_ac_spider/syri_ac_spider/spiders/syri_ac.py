import string
import scrapy
from scrapy import Request
import pandas as pd


class SyriSpider(scrapy.Spider):
    name = 'syri_ac'
    page_number = 1
    start_urls = ['http://syri.ac/digimss/sortable?keys=&items_per_page=100&page=0']
    mss_data = []

    def parse(self, response):
        mss = {}
        page_rows = response.css("tr")
        for row in page_rows:
            ms_name = row.css(".views-field-title a::text").extract()
            ms_lang = row.css(".views-field-field-language::text").extract()
            ms_date = row.css(".views-field-field-ms-approximate-date::text").extract()
            ms_contents = row.css(".views-field-body ul li::text").extract()
            ms_link = row.css(".views-field-field-link-to-digitized-manuscri a").xpath("@href").extract()
            mss.update({'ms name':ms_name,
               'language':ms_lang,
               'date':ms_date,
               'contents':ms_contents,
               'link':ms_link})
        self.mss_data.append(mss)
        yield mss

        next_page = 'http://syri.ac/digimss/sortable?keys=&items_per_page=100&page={}'.format(str(self.page_number))
        if self.page_number < 26:
            self.page_number += 1
            yield response.follow(next_page, callback = self.parse)
        else:
            all_data = pd.DataFrame(self.mss_data)
            all_data.to_csv('syriac_data.csv')
