import scrapy
from ..items import DiscogsAuthorItems, DiscogsAlbumItems, DiscogsSongItems
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose

#Country Search
class DiscogsSpider(scrapy.Spider):
    name = 'discogs'
    allowed_domains = ['www.discogs.com']
    start_urls = [
        'https://www.discogs.com/search/?limit=50&sort=title&country=Serbia&type=all&page=1'
        #'https://www.discogs.com/search/?limit=50&sort=title&country=Yugoslavia&type=all&page=1'
    ]

    # Search - first parse
    def parse(self, response):
        albumCards = response.css('div.cards')

        # Get all Author links from search
        authorLinks = albumCards.css("div.card h5 span a").xpath("@href").extract()
        for authorLink in authorLinks:
            authorLink = response.urljoin(authorLink)
            yield scrapy.Request(url=authorLink, callback=self.author_links)

        # Get all Album links from search
        albumLinks = albumCards.css('div.card h4 a').xpath("@href").extract()
        for albumLink in albumLinks:
            albumLink = response.urljoin(albumLink)
            yield scrapy.Request(url=albumLink, callback=self.album_links)

        # Go to next pages
        # next_page = response.css('ul.pagination_page_links li a.pagination_next::attr("href")').extract_first()
        # if next_page:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(url=next_page, callback=self.parse)
        # if next_page is not None:
        #     return response.follow(next_page, self.parse, priority = 4)

    # Get data from Author links
    def author_links(self, response):
        singleAuthors = response.css('#page_content')
        for singleAuthor in singleAuthors:
            authorItems = DiscogsAuthorItems()
            authorItems['authorName'] = singleAuthor.css('div.profile h1.hide_mobile::text').get()
            authorItems['authorSites'] = singleAuthor.css('.content > a').xpath("@href").get(default='None')
            authorItems['authorCredits'] = singleAuthor.xpath('//a[@data-credit-type="Credits"]/span[1]/text()').get(default='None')
            authorItems['authorVocals'] = singleAuthor.xpath('//a[@data-credit-subtype="Vocals"]/span[1]/text()').get(default='None')
            yield authorItems

    # Get data from Album links
    def album_links(self, response):
        singleAlbums = response.css('#page')
        albumItems = ItemLoader(item = DiscogsAlbumItems(), selector = singleAlbums)
        albumItems.add_xpath('albumId', '//span[@class="copy_shortcut_code"]/text()', MapCompose(lambda i: i.replace('\]', '')))
        albumItems.add_xpath('albumAuthor', '//h1[@id="profile_title"]/span[1]/span/@title',MapCompose(lambda i: i.replace('', '')))
        albumItems.add_xpath('albumName', 'normalize-space(//h1[@id="profile_title"]/span[2]/text())',MapCompose(lambda i: i.replace('\n' '', '')))
        albumItems.add_xpath('albumGenre', '//div[@class="profile"]/div[text()="Genre:"]/following-sibling::div/a/text()')
        albumItems.add_xpath('albumStyle', '//div[@class="profile"]/div[text()="Style:"]/following-sibling::div/a/text()')
        albumItems.add_css('albumYear', '.card .year.has_header::text')
        albumItems.add_css('albumFormat', '.format::text')
        albumItems.add_css('albumCountry', '.card .country.has_header span::text')
        albumItems.add_css('albumSongs', 'td span.tracklist_track_title::text')
        albumItems.add_xpath('albumSongsDuration', '//td[@class="tracklist_track_duration"]/span[1]/text()')
        yield albumItems.load_item()

        # for singleAlbum in singleAlbums:
        #     albumItems = DiscogsAlbumItems()
        #     albumItems['albumId'] = singleAlbum.xpath('//span[@class="copy_shortcut_code"]/text()').get() #.replace('\]', '')
        #     albumItems['albumAuthor'] = singleAlbum.xpath('//h1[@id="profile_title"]/span[1]/span/@title').get()
        #     albumItems['albumName'] = singleAlbum.xpath('normalize-space(//h1[@id="profile_title"]/span[2]/text())').get()
        #     albumItems['albumGenre'] = singleAlbum.xpath('//div[@class="profile"]/div[text()="Genre:"]/following-sibling::div/a/text()').get()
        #     albumItems['albumStyle'] = singleAlbum.xpath('//div[@class="profile"]/div[text()="Style:"]/following-sibling::div/a/text()').get()
        #     albumItems['albumYear'] = singleAlbum.css('.card .year.has_header::text').get()
        #     albumItems['albumFormat'] = singleAlbum.css('.format::text').extract()
        #     albumItems['albumCountry'] = singleAlbum.css('.card .country.has_header span::text').get()
        #     albumItems['albumSongs'] = singleAlbum.css('td span.tracklist_track_title::text').extract()
        #     albumItems['albumSongsDuration'] = singleAlbum.xpath('//td[@class="tracklist_track_duration"]/span[1]/text()').extract()
        #     yield albumItems

        # Get all Songs links from albums
        songLinks = singleAlbums.css("td.tracklist_track_title a").xpath("@href").extract()
        for songLink in songLinks:
            songLink = response.urljoin(songLink)
            yield scrapy.Request(url=songLink, callback=self.song_links)

    # Get data about song (Lyrics, Music, Arranged)
    def song_links(self, response):
        songItems = DiscogsSongItems()
        songItems['songArranged'] = 'None'
        songItems['songMusic'] = 'None'
        songItems['songLyric'] = 'None'
        singleSongs = response.css('.TrackOverview')

        for singleSong in singleSongs:
            songItems['songName'] = singleSongs.css(".TrackTitle h1::text").get()
            txtArranged = singleSong.xpath("string(//h4[text()='arranged by'])").get()
            txtMusic = singleSong.xpath("string(//h4[text()='music by'])").get()
            txtLyrics = singleSong.xpath("string(//h4[text()='lyrics by'])").get()
            # If is not empty
            if bool(txtArranged) == True:
                songItems['songArranged'] = singleSong.xpath("string(//h4[text()='arranged by']/following::div[1]/div[contains(@class, 'title')])").get()

            if bool(txtMusic) == True:
                songItems['songMusic'] = singleSong.xpath("string(//h4[text()='music by']/following::div[1]/div[contains(@class, 'title')])").get()

            if bool(txtLyrics) == True:
                songItems['songLyric'] = singleSong.xpath("string(//h4[text()='lyrics by']/following::div[1]/div[contains(@class, 'title')])").get()

            yield songItems
