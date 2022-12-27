import mysql.connector as connector


def connect_to_MySQL(password):

    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = password,
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    return con, cursor


def insert_publications(cursor, doi, year, journal, authorsKeywords,
    userKeywords, subjects, title, citationsCount):

    for i in range(len(doi)):

        query = 'INSERT INTO publications VALUES (\'' + doi[i] + '\', \'' + year[i] + '\', \'' + journal[i] + '\', \'' + \
            str(authorsKeywords[i]) + '\', \'' + userKeywords[i] + '\', \'' + subjects[i] + '\', \'' + title[i] + '\', \'' + \
            str(citationsCount[i]) + '\');'

        cursor.execute(query)


def insert_authors(cursor, id, eid, orcid, name, hIndex, subjectedAreas, 
    itemCitations, authorsCitations, documentsCount):

    for i in range(len(id)):

        query = 'INSERT INTO authors VALUES (\'' + id[i] + '\', \'' + eid[i] + '\', \'' + orcid[i] + '\', \'' + name[i] + \
            '\', ' + hIndex[i] + ', \'' + subjectedAreas[i] + '\', ' + itemCitations[i] + ', ' + \
            authorsCitations[i] + ', ' + documentsCount[i] + ');'
    
        cursor.execute(query)


def insert_organizations(cursor, id, eid, name, type, address, postalCode, city, state, country):

    for i in range(len(id)):

        query = 'INSERT INTO organizations VALUES (\'' + id[i] + '\', \'' + eid[i] + '\', \'' + name[i] + '\', \'' + type[i] + '\', \'' + \
            address[i] + '\', \'' + postalCode[i] + '\', \'' + city[i] + '\', \'' + state[i] + '\', \'' + country[i] + '\');'

        cursor.execute(query)

def insert_publications_and_authors(cursor, doi, authorID):

    for i in range(len(doi)):
        query = 'INSERT INTO publications VALUES (' + doi[i] + ', ' + authorID[i] + ');'
    
        try:
            cursor.execute(query)
        except:
            continue


def insert_publications_and_organizations(cursor, doi, orgID):

    for i in range(len(doi)):
        query = 'INSERT INTO publications VALUES (' + doi[i] + ', ' + orgID[i] + ');'
    
        try:
            cursor.execute(query)
        except:
            continue


def commit_and_close(connection, cursor):

    connection.commit()
    cursor.close()
    connection.close()