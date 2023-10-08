import mysql.connector as connector

def connect():
    connection = connector.connect(host='localhost',
                                port='3306',
                                user='root',
                                password='gemyl',
                                database="scopus",
                                auth_plugin='mysql_native_password')
    
    return connection, connection.cursor()