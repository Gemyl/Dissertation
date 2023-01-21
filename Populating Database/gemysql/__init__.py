import mysql.connector as connector
from tqdm import tqdm

# connection to a MySQL database
def connect_to_MySQL(password):

    con = connector.connect(host = 'localhost',
                                        port = '3306',
                                        user = 'root',
                                        password = password,
                                        database = 'george',
                                        auth_plugin = 'mysql_native_password')

    cursor = con.cursor()

    
    return con, cursor, connector


# inserting publications data 
def insert_publications(connection, cursor, doi, year, journal, authorsKeywords, userKeywords, subjects, title, citationsCount):

    for i in tqdm(range(len(doi))):
        query = 'INSERT INTO publications VALUES (\'' + doi[i] + '\', ' + year[i] + ', \'' + journal[i] + '\', \'' + \
            authorsKeywords[i] + '\', \'' + userKeywords[i] + '\', \'' + subjects[i] + '\', \'' + title[i] + '\', \'' + \
            citationsCount[i] + '\');'
        try:
            cursor.execute(query)
            connection.commit()

        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue

# inserting authors data
def insert_authors(connection, cursor, id, firstName, lastName, subjectedAreas, hIndex, itemCitations, authorsCitations, documentsCount):

    for i in tqdm(range(len(id))):
        query = 'INSERT INTO authors VALUES (\'' + id[i] + '\', \'' + firstName[i] + '\', \'' + lastName[i] + '\', \'' + \
            subjectedAreas[i] + '\', ' + hIndex[i] + ', ' + itemCitations[i] + ', ' + authorsCitations[i] + ', ' +  \
            documentsCount[i] + ');'
        try:
            cursor.execute(query)
            connection.commit()
            
        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue


# inserting organizations data
def insert_organizations(connection, cursor, id, name, type1, type2, address, postalCode, city, state, country):

    for i in tqdm(range(len(id))):
        try:
            query = 'INSERT INTO organizations VALUES (\'' + id[i] + '\', \'' + name[i] + '\', \'' + type1[i] + '\', \'' + \
                type2[i] + '\', \'' +  address[i] + '\', \'' + postalCode[i] + '\', \'' + city[i] + '\', \'' + \
                state[i] + '\', \'' + country[i] + '\');'
            
            cursor.execute(query)
            connection.commit()

        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue

# insertion of publications and authors identifiers in a relational table
def insert_publications_and_authors(connection, cursor, doi, authorID):

    for i in tqdm(range(len(doi))):
        query = 'INSERT INTO publications_authors (DOI, Author_ID) VALUES (\'' + doi[i] + '\', \'' + authorID[i] + '\');'
        try:
            cursor.execute(query)
            connection.commit()
            
        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue


# insertion of publications and organizations data in a relational table
def insert_publications_and_organizations(connection, cursor, doi, orgID):

    for i in tqdm(range(len(doi))):
        query = 'INSERT INTO publications_organizations (DOI, Organization_ID) VALUES (\'' + doi[i] + '\', \'' + \
        orgID[i] + '\');'
        try:
            cursor.execute(query)
            connection.commit()
            
        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue

def insert_authors_and_organizations(connection, cursor, authorID, orgID):

    for i in tqdm(range(len(authorID))):
        query = 'INSERT INTO authors_organizations (Author_ID, Organization_ID) VALUES (\'' + \
        authorID[i] + '\', \'' + orgID[i] + '\');'
        try:
            cursor.execute(query)
            connection.commit()
            
        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue


def instert_cultural_distances(connection, cursor, doi, citationsCount, minGeoDist, maxGeoDist, avgGeoDist, minOrgDist,
    maxOrgDist, avgOrgDist):

    for i in tqdm(range(len(doi))):
        query = 'INSERT INTO cultural_distances VALUES (\'' + doi[i] + '\', ' + str(citationsCount[i]) + ', ' \
            + minGeoDist[i] + ', ' + maxGeoDist[i] + ', ' + avgGeoDist[i] + ', ' \
            + minOrgDist[i] + ', ' + maxOrgDist[i] + ', ' + avgOrgDist[i] + ');'
        try:
            cursor.execute(query)
            connection.commit()
            
        except connector.Error as err:
            if err.errno not in [1062, 1452]:
                print(f'Query Failed: {query}| Error code {err.errno}: {err.msg}')
            continue

        
# commitment of changes and termination of connection
def commit_and_close(connection, cursor):
    cursor.close()
    connection.close()