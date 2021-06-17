# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy import Spider
from datetime import datetime
from datetime import date
import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy.http import Request


class FinvizScrapingSpider(CrawlSpider):
    name = 'finviz_ticker'
    r = 1
    last_r = 0
    start_urls = ['https://finviz.com/screener.ashx?v=111&o=ticker',
                  # 'https://finviz.com/screener.ashx?v=121&o=ticker',
                  # 'https://finviz.com/screener.ashx?v=131&o=ticker',
                  # 'https://finviz.com/screener.ashx?v=141&o=ticker',
                  # 'https://finviz.com/screener.ashx?v=161&o=ticker',
                  # 'https://finviz.com/screener.ashx?v=171&o=ticker'
                  ]
    tables = {'Overview': '111',
              'Valuation': '121',
              'Ownership': '131',
              'Performance': '141',
              'Financial': '161',
              'Technical': '171'
              }
    allowed_domain = ['finviz.com']
    path = 'trial.csv'  # Config.CONFIG['insider_ticker_scraping']
    all_data = []

    def parse(self, response):
        self.last_r = 61#int(response.xpath('//*[(@id = "pageSelect")]/option/@value')[-1].extract())
        total_pages = int((self.last_r - 1) / 20)
        print(self.last_r)
        print(total_pages)
        urls = []
        current_r = 21
        try:
            page_df = self.get_data(response)
            self.all_data.append(page_df)
        except:
            self.log(f'some problem with response{response}')
        # self.r = self.r + 20
        # next_url = f'{response.url}&r={self.r}'
        for page_number in range(1, total_pages + 1):
            if current_r <= self.last_r:
                urls.append(f'{response.url}&r={str(current_r)}')
                current_r = current_r +20
            else:
                break
        try:
            for url in urls:
                request = response.follow(url, callback=self.parse_pages)
                yield request
        finally:
            df = pd.concat(self.all_data, ignore_index=True)
            df.to_csv('all_data_trial.csv')

        # if self.r < self.last_r:
        #     request = response.follow(next_url, callback=self.parse_pages)
        #     yield request

    def parse_pages(self, response):
        page_df = self.get_data(response)
        self.all_data.append(page_df)
        # self.r = self.r + 20
        # next_url = f'https://finviz.com/screener.ashx?v=121&o=ticker&r={self.r}'
        # if self.r <= self.last_r:
        #     request = response.follow(next_url, callback=self.parse_pages)
        #     yield request
        # else:
        #     df = pd.concat(self.all_data, ignore_index=True)
        #     df.to_csv('all_data_trial.csv')

    def get_data(self, response):
        data = []
        #           this returns all column names: response.css("#screener-content tr:nth-child(4) tr:nth-child(1) td::text").extract()
        base_columns = response.css(
            ".table-top::text").extract()  # this retruns all column names except for the ticker column
        tickers = response.css(".screener-link-primary::text").extract()
        seri = pd.Series(tickers, name='Ticker')
        data.append(seri)
        for column, i in zip(base_columns, range(len(base_columns))):
            col = response.css(".screener-body-table-nw:nth-child({}) .screener-link".format(i + 2))
            col_data = []
            for val in col:
                col_data.append(val.css("::text")[0].extract())
            ser = pd.Series(col_data, name=column)
            data.append(ser)
        table = pd.DataFrame(data).transpose()
        table.drop(['No.'], axis=1, inplace=True)
        return table

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(InsiderScrapingSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    #     return spider
    #
    # def spider_closed(self, spider):
    #     master = pd.DataFrame(self.all_data)
    #     master.to_excel('raw_current_master.xlsx', index_label=False)  # this is the raw master
    #     fixer = Fixer(master, 'SEC', "%b %d %H:%M %p", 'Date', "%b %d")  # "%m/%d/%Y %H:%M", 'Date', "%d-%b")
    #     final_df = fixer.run_fixer()
    #     final_df.drop('creation_time', axis=1, inplace=True)  # remove time column after the clean
    #     final_df.to_excel(Config.CONFIG['insider_master_scraping'].format(date.today()), index=False)
    #     print('finished creating master')
    #
    # def parse(self, response):
    #     data = []
    #     tickers = response.css(".screener-link-primary::text").extract()
    #     seri = pd.Series(tickers, name='Ticker')
    #     data.append(seri)
    #     for column, i in zip(self.base_columns, range(len(self.base_columns))):
    #         col = response.css(".screener-body-table-nw:nth-child({}) .screener-link".format(i + 3))
    #         col_data = []
    #         for val in col:
    #             col_data.append(val.css("::text")[0].extract())
    #         ser = pd.Series(col_data, name=column)
    #         # TODO: add check that number of rows matches length of each columns
    #         data.append(ser)
    #     table = pd.DataFrame(data).transpose()
    #     for ticker in table['Ticker']:
    #         request = Request(self.ticker_url.format(ticker), callback=self.parse_ticker)
    #         request.meta['Ticker'] = ticker
    #         yield request
    #     # check next page
    #     if 'next' in response.css("a.tab-link b::text").extract():
    #         next = response.css("a.tab-link::attr(href)")[-1].extract()
    #         request = Request(self.next_url.format(next), callback=self.parse)
    #         yield request
    #
    # def parse_ticker(self, response):
    #     ticker = response.meta['Ticker']
    #     columns = ['Owner', 'Relationship', 'Date', 'Transaction', 'Cost', '#Shares', 'Value ($)',
    #                '#Shares Total', 'SEC']
    #     cols = []
    #     if len(response.css(".body-table td")) > 0:
    #         for column, i in zip(columns, range(len(columns))):
    #             pattern = ".body-table td:nth-child({})".format(i + 1)
    #             data = []
    #             if len(response.css('{}::text'.format(pattern))[1:]) > 0:
    #                 for val in response.css(pattern)[1:]:
    #                     if len(val.css("::text")) > 0:
    #                         data.append(val.css("::text")[0].extract())
    #                     else:
    #                         data.append('None')
    #             else:
    #                 pattern = ".body-table td:nth-child({}) a::text".format(i + 1)
    #                 data = response.css(pattern)[0:].extract()
    #             ser = pd.Series(data, name=column)
    #             cols.append(ser)
    #         table = pd.DataFrame(cols).transpose()
    #         table['Ticker'] = ticker
    #         table['creation_time'] = datetime.now()
    #         table.to_excel(self.path.format(ticker), index=False)
    #         self.all_data.append(table)
    #     else:
    #         print('{} has no insider data'.format(ticker))
