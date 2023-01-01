import mysql.connector as connector

# connection to a MySQL database
def connect_to_MySQL(password):

    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = password,
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    return con, cursor


# inserting publications data 
def insert_publications(cursor, doi, year, journal, authorsKeywords,
    userKeywords, subjects, title, citationsCount):

    for i in range(len(doi)):

        query = 'INSERT INTO publications VALUES (\'' + doi[i] + '\', \'' + year[i] + '\', \'' + journal[i] + '\', \'' + \
            str(authorsKeywords[i]) + '\', \'' + userKeywords[i] + '\', \'' + subjects[i] + '\', \'' + title[i] + '\', \'' + \
            str(citationsCount[i]) + '\');'

        try:
            cursor.execute(query)
        except:
            continue


# inserting authors data
def insert_authors(cursor, id, eid, orcid, name, hIndex, subjectedAreas, 
    itemCitations, authorsCitations, documentsCount):

    for i in range(len(id)):

        query = 'INSERT INTO authors VALUES (\'' + id[i] + '\', \'' + eid[i] + '\', \'' + orcid[i] + '\', \'' + name[i] + \
            '\', ' + hIndex[i] + ', \'' + subjectedAreas[i] + '\', ' + itemCitations[i] + ', ' + \
            authorsCitations[i] + ', ' + documentsCount[i] + ');'
    
        try:
            cursor.execute(query)
        except:
            continue


# inserting organizations data
def insert_organizations(cursor, id, eid, name, type, address, postalCode, city, state, country):

    for i in range(len(id)):

        query = 'INSERT INTO organizations VALUES (\'' + str(id[i]) + '\', \'' + eid[i] + '\', \'' + name[i] + '\', \'' + type[i] + '\', \'' + \
            address[i] + '\', \'' + postalCode[i] + '\', \'' + city[i] + '\', \'' + state[i] + '\', \'' + country[i] + '\');'

        try:
            cursor.execute(query)
        except:
            continue


# insertion of publications and authors identifiers in a relational table
def insert_publications_and_authors(cursor, doi, authorID):

    for i in range(len(doi)):

        query = 'INSERT INTO publications_authors VALUES (\'' + doi[i] + '\', \'' + authorID[i] + '\');'
    
        try:
            cursor.execute(query)
        except:
            continue


# insertion of publications and organizations data in a relational table
def insert_publications_and_organizations(cursor, doi, orgID):

    for i in range(len(doi)):

        query = 'INSERT INTO publications_organizations VALUES (\'' + doi[i] + '\', \'' + str(orgID[i]) + '\');'

        try:
            cursor.execute(query)
        except:
            continue


def insert_authors_and_publications(cursor, authorID, orgID, curOrgID):

    for i in range(len(authorID)):
        
        query = 'INSERT INTO authors_organizations VALUES (\'' + authorID[i] + '\', \'' + str(orgID[i]) + '\', \'' \
            + curOrgID[i] + '\');'

        try:
            cursor.execute(query)
        except:
            continue

# commitment of changes and termination of connection
def commit_and_close(connection, cursor):

    connection.commit()
    cursor.close()
    connection.close()