import scrapy
from scrapy import Request
from ..items import DiscogsAuthorItems

class DiscogsAuthorSpider(scrapy.Spider):
    name = 'author_spider'
    allowed_domains = ['www.discogs.com']
    start_urls = [
        'https://www.discogs.com/search/?sort=date_changed%2Cdesc&country=Serbia&layout=big&page=1',
        'https://www.discogs.com/search/?sort=date_changed%2Cdesc&country=Serbia&layout=big&page=2',
        'https://www.discogs.com/search/?sort=date_changed%2Cdesc&country=Serbia&layout=big&page=3',
        'https://www.discogs.com/search/?sort=date_changed%2Cdesc&country=Serbia&layout=big&page=4',
        'https://www.discogs.com/search/?sort=date_changed%2Cdesc&country=Serbia&layout=big&page=5'
    ]
    # Search - first parse
    def parse(self, response):
        # Get all Author links from search
        for authorLink in response.css("div.cards div.card h5 span a").xpath("@href").extract():
            authorLink = response.urljoin(authorLink)
            yield scrapy.Request(url=authorLink, callback=self.author_links, dont_filter=False, priority=1)
        # Go to next pages
        next_page = response.css('ul.pagination_page_links li a.pagination_next::attr("href")').extract_first()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)
        if next_page is not None:
            return response.follow(next_page, self.parse)

    # Get data from Author links
    def author_links(self, response):
        singleAuthor = response.css('#page_content')
        authorItems = DiscogsAuthorItems()
        authorItems['authorName'] = singleAuthor.css('div.profile h1.hide_mobile::text').get()
        authorItems['authorSites'] = singleAuthor.css('.content > a').xpath("@href").get(default='None')
        authorItems['authorCredits'] = singleAuthor.xpath('//a[@data-credit-type="Credits"]/span[1]/text()').get(default='None')
        authorItems['authorVocals'] = singleAuthor.xpath('//a[@data-credit-subtype="Vocals"]/span[1]/text()').get(default='None')
        yield authorItems

    # def navigation(self, response):
    #     # Go to next pages
    #     next_page = response.css('ul.pagination_page_links li a.pagination_next::attr("href")').extract_first()
    #     if next_page is not None:
    #         next_page =  response.urljoin(next_page)
    #         return scrapy.Request(next_page, callback=self.parse)