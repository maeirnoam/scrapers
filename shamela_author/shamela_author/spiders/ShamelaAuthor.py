# -*- coding: utf-8 -*-
import scrapy


class ShamelaAuthorSpider(scrapy.Spider):
    name = 'author'
    author_id = '1139'
    start_urls = ['https://al-maktaba.org/author/{}'.format(author_id)]

    def parse(self, response):
        author_links = response.css("a::attr(href)").extract()
        books = []
        for link in author_links:
            if 'book/' in link:
                books.append(link)
        for book in books:
            yield response.follow(book, callback=self.parse_book)

        self.log('extracted page {}'.format(self.page_name))


    def parse_book(self, response):
        author = response.css(".text-center + div a::text").extract()
        first_page = response.css(".betaka-index a::attr(href)").extract_first()
        bib = response.css("div.nass::text").extract()
        bib_text = bib[1]

        page_text = ''
        paras = response.css("p")
        for para in paras[:-5]:
            para_text = ''
            lines = para.css("::text").extract()
            for line in lines:
                para_text = para_text + ' ' + line
            page_text = page_text + para_text + '\n'
        self.all_text = self.all_text + 'page: ' + str(self.page_name) + '\n\n' + page_text + '\n'

        next_page = response.css("#fld_goto_bottom+ .btn-sm::attr(href)").get()

        if next_page is not None:  # self.page_number < self.last_page:
            self.page_number += 1
            self.page_name += 1
            yield response.follow(next_page, callback=self.parse)
        else:
            text_file = open("{}, {}.text".format(self.title, self.author), "w")
            text_file.write(self.all_text)
            text_file.close()


