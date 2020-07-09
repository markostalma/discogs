# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import NotConfigured, DropItem
import mysql
from mysql.connector import connection

from .items import DiscogsAuthorItems, DiscogsAlbumItems, DiscogsSongItems

class DiscogsPipeline(object):
    def __init__(self, database, user, password, host, auth_plugin):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.auth_plugin = auth_plugin
        self.ids_seen = set()

    @classmethod
    # Get data for database from settings
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured
        database = db_settings['database']
        user = db_settings['user']
        password = db_settings['password']
        host = db_settings['host']
        auth_plugin = db_settings['auth_plugin']
        return cls(database, user, password, host, auth_plugin)

    # Close cursor and return new connection
    def refresh_cursor(self, cursor, conn):
        self.cursor.close()
        return self.conn.cursor()

    # Make connection with database and create all tables
    def open_spider(self, spider):
        # Make connection
        self.conn = connection.MySQLConnection(
                               database=self.database,
                               user=self.user,
                               password=self.password,
                               host=self.host,
                               auth_plugin=self.auth_plugin,
                               charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

        # Author Table
        self.cursor.execute("""DROP TABLE IF EXISTS author""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS author ('
                       'AuthorId INT AUTO_INCREMENT,'
                       'AuthorName NVARCHAR(200),'
                       'AuthorSites NVARCHAR(200),'
                       'AuthorVocals NVARCHAR(200),'
                       'AuthorCredits NVARCHAR(200),'
                       'PRIMARY KEY(AuthorId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Album Table
        self.cursor.execute("""DROP TABLE IF EXISTS album""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS album ('
                       'Id INT AUTO_INCREMENT,'
                       'AuthorId NVARCHAR(200),'
                       'AlbumId NVARCHAR(200) ,'
                       'AlbumName NVARCHAR(200),'
                       'AlbumYear INT,'
                       'AlbumVersions INT,'
                       'PRIMARY KEY(Id)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Country Table
        self.cursor.execute("""DROP TABLE IF EXISTS country""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS country ('
                       'CountryId INT AUTO_INCREMENT,'
                       'CountryName NVARCHAR(100) NOT NULL,'
                       'PRIMARY KEY(CountryId)'
                       ');')

        # Album and Country Join Table
        self.cursor.execute("""DROP TABLE IF EXISTS album_country""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS album_country ('
                       'AlbumId NVARCHAR(200),'
                       'CountryId INT,'
                       'PRIMARY KEY (CountryId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Album and Version Join Table
        self.cursor.execute("""DROP TABLE IF EXISTS album_version""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS album_version ('
                       'VersionId INT AUTO_INCREMENT,'
                       'AlbumId NVARCHAR(200),'
                       'VersionFormat NVARCHAR(50),'
                       'PRIMARY KEY(VersionId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Music Genre Table
        self.cursor.execute("""DROP TABLE IF EXISTS genre""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS genre ('
                       'GenreId INT AUTO_INCREMENT,'
                       'GenreName NVARCHAR(50) NOT NULL,'
                       'PRIMARY KEY(GenreId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Album and Music Genre Join Table
        self.cursor.execute("""DROP TABLE IF EXISTS album_genre""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS album_genre ('
                       'AlbumId NVARCHAR(200),'
                       'GenreId INT,'
                       'PRIMARY KEY (GenreId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Music Style Join Table
        self.cursor.execute("""DROP TABLE IF EXISTS style""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS style ('
                       'StyleId INT AUTO_INCREMENT,'
                       'StyleName NVARCHAR(30) NOT NULL,'
                       'PRIMARY KEY(StyleId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Album and Music Style Join Table
        self.cursor.execute("""DROP TABLE IF EXISTS album_style""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS album_style ('
                       'AlbumId NVARCHAR(200),'
                       'StyleId INT,'
                       'PRIMARY KEY (StyleId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Song Table
        self.cursor.execute("""DROP TABLE IF EXISTS song""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS song ('
                       'SongId INT AUTO_INCREMENT,'
                       'AlbumId NVARCHAR(200),'
                       'Songs NVARCHAR(200),'
                       'SongsDurations NVARCHAR(200),'
                       'ArrangedBy NVARCHAR(60),'
                       'MusicBy NVARCHAR(60),'
                       'LyricBy NVARCHAR(60),'
                       'PRIMARY KEY (SongId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

    # Process all items to database
    def process_item(self, item, spider):
        if isinstance(item, DiscogsAuthorItems):
            self.store_author_to_db(item, spider)
        if isinstance(item, DiscogsAlbumItems):
            self.store_album_to_db(item, spider)
        if isinstance(item, DiscogsSongItems):
            self.store_song_to_db(item, spider)

     # Insert all into author table
    def store_author_to_db(self, item, spider):
        try:
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute("INSERT INTO author (AuthorName, AuthorSites, AuthorVocals, AuthorCredits) VALUES (%s, %s, %s, %s) ", (
                str(item.get("authorName")),
                str(item.get("authorSites")),
                str(item.get("authorVocals")),
                str(item.get("authorCredits")),
                ))
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

    # Insert album detail to db
    def store_album_to_db(self, item, spider):
        # Country Unique List
        countries = []
        for country in item['albumCountry']:
            if country not in countries:
                countries.append(country)
        try:
            # Album Country
            for country in countries:
                self.cursor = self.refresh_cursor(self.cursor, self.conn)
                self.cursor.execute('INSERT INTO country (CountryName)'
                                    ' VALUES (\'' + str(country) + '\')')
            # Album Genre
            for genreName in item.get('albumGenre'):
                self.cursor = self.refresh_cursor(self.cursor, self.conn)
                self.cursor.execute('INSERT INTO genre (GenreName)'
                                    ' VALUES (\'' + str(genreName) + '\')')
            # Album Style
            for styleName in item.get('albumStyle'):
                self.cursor = self.refresh_cursor(self.cursor, self.conn)
                self.cursor.execute('INSERT INTO style (StyleName)'
                                    ' VALUES (\'' + str(styleName) + '\')')
            # Album Format
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            for formatName in item.get('albumFormat'):
                self.cursor.execute("INSERT INTO album_version (AlbumId, VersionFormat) VALUES (%s, %s)", (
                    str(item.get("albumId")),
                    str(formatName)
                ))
            # Song Detail
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            for i, songs in enumerate(item.get("albumSongs")):
                songsDuration = int(item['albumSongsDuration'][i].split(':')[0]) * 60 + int(item['albumSongsDuration'][i].split(':')[1])
                self.cursor.execute("INSERT INTO song (AlbumId, Songs, SongsDurations) VALUES (%s, %s, %s)", (
                    str(item.get("albumId")),
                    str(songs),
                    str(songsDuration)
                ))
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

        # Album Detail
        try:
            query = "INSERT INTO Album (albumId, AlbumName, AlbumYear, AlbumVersions, AuthorId) VALUES ('" + str(item.get("albumId"))  + "','" + str(item.get("albumName"))  + "','" + str(item.get("albumYear")) + "','" + str(len(item.get("albumFormat"))) + "',(SELECT AuthorId FROM author WHERE AuthorName ='" + str(item.get("albumAuthor")) + "'))"
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

        # try:
        #     # album_country table
        #     for country in countries:
        #         self.cursor = self.refresh_cursor(self.cursor, self.conn)
        #         query = "INSERT INTO album_country (AlbumId, CountryId) VALUES ('" + str(item.get("albumId")) + "',(SELECT CountryId FROM country WHERE CountryName = '" + str(country) + "'))"
        #         self.cursor.execute(query)
        #     # album_style table
        #     for style in item.get('albumStyle'):
        #         self.cursor = self.refresh_cursor(self.cursor, self.conn)
        #         self.cursor.execute('INSERT INTO album_style (AlbumId, StyleId) VALUES (' + str(item.get("albumId")) + ','
        #                             '(SELECT StyleId FROM style WHERE StyleName = \'' + str(style) + '\'))')
        #     # album_genre table
        #     for genre in item.get('albumGenre'):
        #         self.cursor = self.refresh_cursor(self.cursor, self.conn)
        #         self.cursor.execute('INSERT INTO album_genre (AlbumId, GenreId) VALUES (' + str(item.get("albumId")) + ','
        #                             '(SELECT GenreId FROM genre WHERE GenreName = \'' + str(genre) + '\'))')
        #
        # except mysql.connector.Error as err:
        #     print(err)
        #self.conn.commit()

    # Insert song detail to db
    def store_song_to_db(self, item, spider):
        # Songs Detail update
        query = "UPDATE song SET ArrangedBy = '" + str(item.get("songArranged")) + "', MusicBy = '" + str(item.get("songMusic"),) + "', LyricBy = '" + str(item.get("songLyric")) + "' WHERE Songs = '" + str(item.get("songName")) + "'"
        try:
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

    # Close connection after finish
    def close_spider(self, spider):
        self.conn.close()
