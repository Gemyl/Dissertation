from sqlalchemy import create_engine
import mysql.connector as connector


def InsertDataFrame(dataFrame, name):
    engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                        .format(user='root',
                                pw='gemyl',
                                db='george'))

    dataFrame.to_sql(name, con=engine, if_exists='append',chunksize=1000)


def CountAuthors(tableName):
    standardColumns = 9
    database = 'george'

    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = 'gemyl',
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    query = 'SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s'
    cursor.execute(query, (database, tableName))

    count = (cursor.fetchone()[0] - standardColumns)/2

    cursor.close()
    con.close()

    return count

def AddAuthors(tableName, newNumAuthors, oldNumAuthors):
    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = 'gemyl',
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