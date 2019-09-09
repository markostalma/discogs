import scrapy
import re
from ..items import DiscogsAlbumItems, DiscogsSongItems
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose

class DiscogsAlbumSpider(scrapy.spiders.CrawlSpider):
    name = 'album_spider'
    allowed_domains = ['www.discogs.com']
    start_urls = [
        'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=1',
        'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=2',
        'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=3',
        'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=4',
        'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=5'
    ]
    # Search - first parse
    def parse(self, response):
        albumCards = response.css('div.cards')
        # Get all Album links from search
        albumLinks = albumCards.css('div.card h4 a').xpath("@href").extract()
        for albumLink in albumLinks:
            albumLink = response.urljoin(albumLink)
            yield scrapy.Request(url=albumLink, callback=self.album_links, dont_filter=False)

        # Go to next pages
        next_page = response.css('ul.pagination_page_links li a.pagination_next::attr("href")').extract_first()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse, dont_filter=False)
        if next_page is not None:
            return response.follow(next_page, self.parse)

    # Get data from Album links
    def album_links(self, response):
        singleAlbums = response.css('#page')
        albumItems = DiscogsAlbumItems()
        albumItems['albumId'] = singleAlbums.xpath('//span[@class="copy_shortcut_code"]/text()').get() #.replace('\]', '')
        albumItems['albumAuthor'] = singleAlbums.xpath('//h1[@id="profile_title"]/span[1]/span/@title').get()
        albumItems['albumName'] = singleAlbums.xpath('normalize-space(//h1[@id="profile_title"]/span[2]/text())').get()
        albumItems['albumGenre'] = singleAlbums.xpath('//div[@class="profile"]/div[text()="Genre:"]/following-sibling::div/a/text()').get()
        albumItems['albumStyle'] = singleAlbums.xpath('//div[@class="profile"]/div[text()="Style:"]/following-sibling::div/a/text()').get()
        albumItems['albumYear'] = singleAlbums.css('.card .year.has_header::text').get()
        albumItems['albumFormat'] = singleAlbums.css('.format::text').extract()
        albumItems['albumCountry'] = singleAlbums.css('.card .country.has_header span::text').get()
        albumItems['albumSongs'] = singleAlbums.css('td span.tracklist_track_title::text').extract()
        albumItems['albumSongsDuration'] = singleAlbums.xpath('//td[@class="tracklist_track_duration"]/span[1]/text()').extract()
        yield albumItems
        # Get all Songs links from albums
        # songLinks = singleAlbums.css("td.tracklist_track_title a").xpath("@href").extract()
        # for songLink in songLinks:
        #     songLink = response.urljoin(songLink)
        #     yield scrapy.Request(url=songLink, callback=self.song_links, dont_filter=False)

    # Get data about song (Lyrics, Music, Arranged)
    def song_links(self, response):
        # print("song parsed: " + response.url)
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
            # If not empty
            if bool(txtArranged) == True:
                songItems['songArranged'] = singleSong.xpath("string(//h4[text()='arranged by']/following::div[1]/div[contains(@class, 'title')])").get()

            if bool(txtMusic) == True:
                songItems['songMusic'] = singleSong.xpath("string(//h4[text()='music by']/following::div[1]/div[contains(@class, 'title')])").get()

            if bool(txtLyrics) == True:
                songItems['songLyric'] = singleSong.xpath("string(//h4[text()='lyrics by']/following::div[1]/div[contains(@class, 'title')])").get()
            yield songItems