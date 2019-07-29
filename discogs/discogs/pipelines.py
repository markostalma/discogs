# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import NotConfigured, DropItem
from scrapy.exporters import CsvItemExporter
import mysql
from mysql.connector import connection

class CsvPipeline(object):
    def __init__(self):
        self.file = open("discogs.csv", 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8',)
        self.exporter.start_exporting()

    # def create_valid_csv(self, item):
    #     for key, value in item.items():
    #         is_string = (isinstance(value, basestring))
    #         if (is_string and ("," in value.encode('utf-8'))):
    #             item[key] = "\"" + value + "\""

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    # def process_item(self, item, spider):
    #     self.exporter.export_item(item)
    #     return item


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
                       'AlbumId INT,'
                       'CountryId INT,'
                       'PRIMARY KEY (AlbumId, CountryId)'
                       ');')
        self.cursor = self.refresh_cursor(self.cursor, self.conn)

        # Album and Version Join Table
        self.cursor.execute("""DROP TABLE IF EXISTS album_version""")
        self.cursor.execute('CREATE TABLE IF NOT EXISTS album_version ('
                       'VersionId INT AUTO_INCREMENT,'
                       'AlbumId INT,'
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
                       'AlbumId INT,'
                       'GenreId INT,'
                       'PRIMARY KEY (AlbumId, GenreId)'
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
                       'AlbumId INT,'
                       'StyleId INT,'
                       'PRIMARY KEY (AlbumId, StyleId)'
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

     # Insert all into author table
    def store_author_to_db(self, item):
        try:
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute(""" INSERT INTO author (AuthorName, AuthorSites, AuthorVocals, AuthorCredits) VALUES (%s, %s, %s, %s) """, (
                item.get("authorName"),
                item.get("authorSites"),
                item.get("authorVocals"),
                item.get("authorCredits"),
                ))
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

    # Insert album detail to db
    def store_album_to_db(self, item):
        # try:
        #     # Album Genre
        #     self.cursor = self.refresh_cursor(self.cursor, self.conn)
        #     self.cursor.execute('INSERT INTO genre (GenreName)'
        #                         ' VALUES (\'' + str(item.get('albumGenre')) + '\')')
        #                         #' VALUES (\'' + str(item.get('albumGenre')) + '\')')
        #     # Album Style
        #     self.cursor = self.refresh_cursor(self.cursor, self.conn)
        #     self.cursor.execute('INSERT INTO style (StyleName)'
        #                         ' VALUES (\'' + str(item.get('albumStyle')) + '\')')
        #     # Album Style
        #     self.cursor = self.refresh_cursor(self.cursor, self.conn)
        #     self.cursor.execute('INSERT INTO country (CountryName)'
        #                         ' VALUES (\'' + str(item.get('albumCountry')) + '\')')
        # except mysql.connector.Error as err:
        #     print(err)
        # Album Detail
        try:
            query = "INSERT INTO Album (albumId, AuthorId) VALUES ('" + str(item.get("albumId"))  + "',(SELECT AuthorId FROM author WHERE AuthorName ='" + str(item.get("albumAuthor")) + "'))"
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err)
        # Song Detail
        try:
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute("INSERT INTO song (AlbumId, Songs, SongsDurations) VALUES (%s, %s, %s)", (
                    item.get("albumId"),
                    item.get("albumSongs"),
                    item.get("albumSongsDuration")
                ))
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

    # Insert song detail to db
    def store_song_to_db(self, item):
        # Songs Detail
        query = "UPDATE song SET ArrangedBy = '" + str(item.get("songArranged")) + "', MusicBy = '" + str(item.get("songMusic"),) + "', LyricBy = '" + str(item.get("songLyric")) + "' WHERE Songs = '" + str(item.get("songName")) + "'"
        try:
            self.cursor = self.refresh_cursor(self.cursor, self.conn)
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err)
        self.conn.commit()

    # Process all items to database
    def process_item(self, item, spider):
        self.store_author_to_db(item)
        self.store_album_to_db(item)
        self.store_song_to_db(item)
        # if 'albumGenre' not in item:
        #     print('-' * 60)
        #     print('"albumGenre has not been given a value"')
        #     print('-' * 60)
        return item

    # Close connection after finish
    def close_spider(self, spider):
        self.conn.close()