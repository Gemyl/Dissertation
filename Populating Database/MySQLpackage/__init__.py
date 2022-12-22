from sqlalchemy import create_engine
import mysql.connector as connector
import re


def insert_to_MySQL(dataFrame, name, password):
    engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                        .format(user='root',
                                pw=password,
                                db='george'))

    dataFrame.to_sql(name, con=engine, if_exists='append',chunksize=1000)


def add_authors(tableName, password, newNumAuthors, oldNumAuthors):
    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = password,
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    query = 'ALTER TABLE ' + tableName + ' '
    for i in range(oldNumAuthors, newNumAuthors):
        if i != newNumAuthors-1:
            query = query + 'ADD COLUMN Author_' + str(i+1) + '_ID VARCHAR(15), '
            query = query + 'ADD COLUMN Author_' + str(i+1) + '_Name VARCHAR(50), '
        else:
            query = query + 'ADD COLUMN Author_' + str(i+1) + '_ID VARCHAR(15), '
            query = query + 'ADD COLUMN Author_' + str(i+1) + '_Name VARCHAR(50);'
    
    cursor.execute(query)

    cursor.close()
    con.close()


def find_authors_number(tableName, password):
    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = password,
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    query = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;'
    cursor.execute(query, ('george', tableName))
    columnNames = [row[0] for row in cursor.fetchall()]

    counter = 0
    for col in columnNames:
        try:
            num = int(re.findall(r'\d+', col)[0])
            if num > counter:
                counter += 1
        except:
            continue

    cursor.close()
    con.close()

    return counter


def remove_nulls(tableName, password):

    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = password,
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    query = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;'
    cursor.execute(query, ('george', tableName))
    columnNames = [row[0] for row in cursor.fetchall()]

    for col in columnNames:
        if col != 'index':
            query = 'UPDATE ' + tableName + ' SET ' + col + ' = COALESCE(' + col + ', \' \') WHERE ' + col + ' IS NULL;'
            cursor.execute(query)

    cursor.close()
    con.commit()
    con.close()