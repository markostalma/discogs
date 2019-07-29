from mysql.connector import connection


def get_connection():
    user = 'user1'
    password = 'password'
    db = 'scrapy_results'

    host = '127.0.0.1'
    port = 3306
    return connection.MySQLConnection(user=user,
                                      password=password,
                                      database=db,
                                      host=host,
                                      port=port,
                                      auth_plugin='mysql_native_password')
