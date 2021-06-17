import string
import scrapy
from scrapy import Request
import pandas as pd


class ShamelaSpider(scrapy.Spider):
    name = 'shamela_book'
    author_eng = "Abu Nu'aym"
    title_eng = "Hilyat al-Awliya"
    start_urls = ["https://al-maktaba.org/book/33728"] #
    all_text = ''

    def parse(self, response):
        author = response.css(".page-header-sm .container div a::text")[0].extract()
        title = response.css(".text-primary::text").extract_first()
        bib = response.css("div.nass::text").extract()
        bib_text = bib[1]
        all_text = '' + bib_text
        bib_data = {'author': author, 'title': title, 'bib data': bib_text, 'all_text': all_text}
        tries = 4
        for i in range(tries):
            try:
                first_page = response.css(".betaka-index a::attr(href)")[i].extract()
                request = Request(first_page, callback=self.parse_pages)
                request.meta['meta'] = bib_data
                yield request
            except:
                self.log('some problem with first page html')


    def parse_pages(self, response):
        bib_data = response.meta['meta']
        page_text = ''
        paras = response.css("p")
        page_name = response.css("#fld_goto_top::attr(value)")[0].extract()

        for para in paras[:-5]:
            para_text = ''
            lines = para.css("::text").extract()
            for line in lines:
                para_text = para_text + ' ' + line
            page_text = page_text + para_text + '\n'
        bib_data['all_text'] = bib_data['all_text'] + 'page: ' + str(page_name) + '\n\n' + page_text + '\n'
        self.log('extracted page {} from book {}'.format(page_name, response.url))
        next_page = response.css("#fld_goto_bottom+ .btn-sm::attr(href)").get()

        if next_page is not None:
            response.meta['meta'] = bib_data
            request = response.follow(next_page, callback=self.parse_pages)
            request.meta['meta'] = bib_data
            yield request
        else:
            text_file = open("{}, {}.txt".format(bib_data['title'], self.author_eng), "w")
            text_file.write(bib_data['all_text'])
            text_file.close()
