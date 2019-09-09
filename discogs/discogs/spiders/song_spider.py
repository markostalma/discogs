import scrapy
from ..items import DiscogsSongItems

class DiscogsAlbumSpider(scrapy.Spider):
    name = 'song_spider'
    allowed_domains = ['www.discogs.com']
    start_urls = [
        'https://www.discogs.com/search/?sort=score%2Cdesc&country=Serbia&layout=big',
        # 'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=2',
        # 'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=3',
        # 'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=4',
        # 'https://www.discogs.com/search/?sort=title%2Cdesc&country=Serbia&layout=big&page=5'
    ]
    # Search - first parse
    def parse(self, response):
        albumCards = response.css('div.cards')
        # Get all Album links from search
        albumLinks = albumCards.css('div.card h4 a').xpath("@href").extract()
        for albumLink in albumLinks:
            albumLink = response.urljoin(albumLink)
            print('-' * 30)
            print(albumLink)
            print('-' * 30)
            # Get all Songs links from albums
            # singleAlbums = albumLink.css('#page')
            print('-' * 30)
            print(singleAlbums)
            print('-' * 30)
            songLinks = singleAlbums.css("td.tracklist_track_title a").xpath("@href").extract()
            print('-' * 30)
            print(songLinks)
            print('-' * 30)
            for songLink in songLinks:
                songLink = response.urljoin(songLink)
                yield scrapy.Request(url=songLink, callback=self.song_links, dont_filter=False)

        # Go to next pages
        # next_page = response.css('ul.pagination_page_links li a.pagination_next::attr("href")').extract_first()
        # if next_page:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(url=next_page, callback=self.parse, dont_filter=False)
        # if next_page is not None:
        #     return response.follow(next_page, self.parse)

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