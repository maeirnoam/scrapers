import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request


class MySpider(CrawlSpider):
    name = 'author_scrape'
    author_id = '249'
    author_eng = "Ibn Qutayba"
    start_urls = ['https://al-maktaba.org/author/{}'.format(author_id)]

    rules = (
        # Extract links matching 'book/' and parse them with the spider's method parse_book
        Rule(LinkExtractor(allow=('book/',)), callback='parse_book'),
    )

    def parse_book(self, response):
        author = response.css(".page-header-sm .container div a::text")[0].extract()
        title = response.css(".text-primary::text").extract_first()
        bib = response.css("div.nass::text").extract()
        bib_text = bib[1]
        all_text = '' + bib_text
        bib_data = {'author': author, 'title': title, 'bib data': bib_text, 'all_text': all_text}
        first_page = response.css(".betaka-index a::attr(href)").extract_first()
        first_page_alt = response.css(".betaka-index a::attr(href)")[1].extract()
        try:
            request = Request(first_page, callback=self.parse_pages)
            request.meta['meta'] = bib_data
            yield request
        except:
            request = Request(first_page_alt, callback=self.parse_pages)
            request.meta['meta'] = bib_data
            yield request

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
            text_file = open("{}, {}.txt".format(bib_data['title'], self.author_eng), "w", encoding='utf-8')
            text_file.write(bib_data['all_text'])
            text_file.close()

