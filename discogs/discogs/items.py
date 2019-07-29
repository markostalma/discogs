# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Compose, Join
from w3lib.html import replace_escape_chars, remove_tags, strip_html5_whitespace

class DiscogsAuthorItems(scrapy.Item):
    authorName = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    authorSites = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    authorVocals = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    authorCredits = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )

class DiscogsAlbumItems(scrapy.Item):
    albumId = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    albumAuthor = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    albumName = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars,  strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    albumGenre = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        #output_processor=Join(',')
    )
    albumStyle = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=Join(',')
    )
    albumYear = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=Join(',')
    )
    albumFormat = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=Join(',')
    )
    albumCountry = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=Join(',')
    )
    albumSongs = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace)
    )
    albumSongsDuration = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace)
    )

class DiscogsSongItems(scrapy.Item):
    songName = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    songLyric = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    songMusic = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
    songArranged = scrapy.Field(
        input_processor=MapCompose(remove_tags, replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst()
    )
