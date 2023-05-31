import mysql.connector as connector
from getpass import getpass


def connect():
    password = getpass('Password:')
    connection = connector.connect(host='localhost',
                                port='3306',
                                user='root',
                                password=password,
                                database="scopus",
                                auth_plugin='mysql_native_password')
    
    return connection, connection.cursor()