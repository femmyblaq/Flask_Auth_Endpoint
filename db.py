import os
from dotenv import load_dotenv
import pymysql
from config import Config

def get_connection():
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        port=Config.MYSQL_PORT,
        cursorclass=pymysql.cursors.DictCursor
        # ssl=Config.SSL
    )
    return connection
