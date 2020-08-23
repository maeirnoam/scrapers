import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
import re

class MySpider(CrawlSpider):
    name = 'author_scrape'
    author_name = 'أبي طالب المكي'
    author_eng = 'al-Makki'
    start_urls = ['https://ablibrary.net/books/?offset=0&limit=50&author={}&sort=name,asc'.format(author_name)]#start url from here, need to parse the json dict.


    def parse(self, response):
        author_data = response.body.decode()
        books_ptrn = re.compile(r'"(author":.+?id":(\d+?),.+?"name":" (.+?)".+?"volume":"(.+?)"})',
                                re.DOTALL | re.MULTILINE | re.UNICODE)
        books = re.findall(books_ptrn, author_data)
        for book in books:
            bib = book[0]
            book_id = book[1]
            title = book[2]

            all_text = '' + bib
            bib_data = {'author': self.author_eng, 'title': title, 'bib data': bib, 'all_text': all_text}
            volume = book[3]
            if volume != ' ':
                bib_data['title'] = bib_data['title']+'v.' + volume
            book_url = 'https://ablibrary.net/books/{}/content?fields=content,footnote,description,page_name,' \
                       'page_number'.format(book_id)
            request = Request(book_url, callback=self.parse_book)
            request.meta['meta'] = bib_data
            yield request

    def parse_book(self, response):
        bib_data = response.meta['meta']
        book_text = response.body.decode()
        bib_data['all_text'] = bib_data['all_text'] + '\n' + book_text
        self.log('extracted book {}'.format(bib_data['title']))
        text_file = open("{}, {}.txt".format(bib_data['title'], self.author_eng), "w")
        #bib_data['all_text'] = self.clean_text(bib_data['all_text'])
        text_file.write(bib_data['all_text'])
        text_file.close()

    def clean_text(self, text):
        #here will be code that removes from the string "text" the unwanted patterns
        return text

