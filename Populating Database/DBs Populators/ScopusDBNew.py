from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval, PlumXMetrics
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
import mysql.connector as connector
from itertools import combinations
from statistics import mean
from requests import get
from tqdm import tqdm
from getpass import getpass
import json
import uuid


# build a proper keyword request query
def buildKeywordsQuery(keywords):
    keywords = keywords.split(', ')
    keywordsList = '('
    for i in range(len(keywords)):
        if i == len(keywords)-1:
            keywordsList = keywordsList + '{' + keywords[i] + '}'
        else:
            keywordsList = keywordsList + '{' + keywords[i] + '} ' + 'OR '

    keywordsList = keywordsList + ')'
    keywords = keywordsList
    return keywords


# get string from list
def getStringFromList(list):
    if list != None:
        string = ', '.join([str(i).lower() for i in list])
    else:
        string = ' '
    return string


# get geographical distances
def getGeoDistance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Apply the Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius of Earth in kilometers
    r = 6371

    # Return the distance in kilometers
    return c * r


# get columns length
def getColumnLength(column, table, cursor):
    try:
        query = f"SELECT MAX(LENGTH({column})) FROM {table};"
        cursor.execute(query)
        result_set = cursor.fetchall()
        return result_set[0][0]
    except:
        return 100


# replace "'" with "\'" for valid SQL syntax
def replaceSingleQuote(string):
    if string != None:
        return string.replace("\'", "\\\'")
    else:
        return "-"


# remove common words
def removeCommonWords(abstract, commonWords):
    abstractList = abstract.split(" ")
    abstractString = " ".join(
        [word for word in abstractList if word.lower() not in commonWords])
    return abstractString


# get maximum citations count
def getMaximumCitationsCount(citationsCount, doi):
    maxCitations = citationsCount
    plumxCitations = PlumXMetrics(doi, id_type='doi').citation

    if plumxCitations != None:
        plumxCitations = max([citation[1] for citation in plumxCitations])
        maxCitations = max(maxCitations, plumxCitations)

    return maxCitations


# get safely abstract
def getAbstract(abstract, description):
    if abstract != None:
        return replaceSingleQuote(abstract)
    elif description != None:
        return replaceSingleQuote(description)
    else:
        return "-"


# get safely keywords
def getKeywords(keywords):
    if keywords != None:
        return replaceSingleQuote(", ".join([keyword for keyword in keywords]))
    else:
        return "-"


# get safely fields
def getFields(fields):
    if fields != None:
        return replaceSingleQuote(", ".join([field[0].lower() for field in fields]))
    else:
        return "-"


# get author's affiliations
def getAffiliations(affiliations):

    affilHistory = []
    for affil in affiliations:
        if (affil[1] == None) & (affil[5] not in affilHistory):
            affilHistory.append(affil[5])
        elif (affil[5] not in affilHistory):
            affilHistory.append(affil[5] + ' - ' + affil[6])
            affilHistory.append(affil[6])

    affilHistoryStr = ', '.join(affilHistory).replace("\'", "\\\'")

    return replaceSingleQuote(affilHistoryStr)


# search parameters
keywords = 'ai'
yearPublished = '2022'
fields = ['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
          'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
          'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
          'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']
fields = ['SOCI']

# list of common words in order to be removed from abstracts
commonWords = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about',
               'to', 'from', 'in', 'on', 'up', 'out', 'as', 'into', 'through', 'over', 'after', 'under',
               'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'has', 'had',
               'will', 'be', 'not', 'would', 'should', 'before', 'few', 'many', 'much', 'so', 'furthermore']

# password for MySQL DB
database = getpass('Database:')
password = getpass('Password: ')

# establishing connection to database
connection = connector.connect(host='localhost',
                               port='3306',
                               user='root',
                               password=password,
                               database=database,
                               auth_plugin='mysql_native_password')
cursor = connection.cursor()

# getting columns size
titleLength = getColumnLength('Title', 'scopus_publications', cursor)
abstractLength = getColumnLength('Abstract', 'scopus_publications', cursor)
keywordsLength = getColumnLength('Keywords', 'scopus_publications', cursor)
fieldsLength = getColumnLength('Fields', 'scopus_publications', cursor)
fieldsOfStudyLength = getColumnLength(
    'Fields_Of_Study', 'scopus_authors', cursor)
affiliationsLength = getColumnLength('Affiliations', 'scopus_authors', cursor)

# upper limit for columns size
MAX_COLUMN_SIZE = 1500

# loading IDs matching JSON file


# query parameters
count = '&count=25'
term1 = '( {python} )'
term2 = buildKeywordsQuery(keywords)
terms = f'( {term1} AND {term2} )'
scope = 'TITLE-ABS-KEY'
view = '&view=standard'
sort = '&sort=citedby_count'
date = '&date=' + str(yearPublished)
scopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'
scopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

# lists and dictionaries
dois = []
uniqueDois = []
citationsCount = []
scopusPublicationsIds = {}
scopusAuthorsIds = {}

# retrieving publications DOIs
print("Retrieving DOIs ...")
for field in tqdm(fields):

    startIndex = 0
    while True:
        start = f"&start={startIndex}"
        currentField = f"&subj={field}"
        # building GET query
        query = 'query=' + scope + terms + date + start + \
            count + sort + currentField + scopusAPIKey + view
        url = scopusBaseUrl + query

        req = get(url)
        # if request is successful, get DOIs
        if req.status_code == 200:
            content = json.loads(req.content)['search-results']
            totalResults = int(content['opensearch:totalResults'])
            startIndex = int(content['opensearch:startIndex'])
            metadata = content['entry']
        # else print the error cause
        else:
            Error = json.loads(req.content)['service-error']['status']
            print(req.status_code, Error['statusText'])

        for md in metadata:
            try:
                TempDOI = md['prism:doi']
                dois.append(str(TempDOI))
            except:
                pass

        remainingData = totalResults - startIndex - len(metadata)

        # if there are any records remained, update startIndex and start the next loop
        if remainingData > 0:
            startIndex += 25
        # else exit the loop and continue with the next subject
        else:
            break

# getting each publication's metadata through its DOI
print("Getting metadata ...")
for doi in tqdm(dois):

    id = str(uuid.uuid4())
    year = yearPublished
    title = replaceSingleQuote(AbstractRetrieval(doi).title)
    abstract = getAbstract(AbstractRetrieval(
        doi).abstract, AbstractRetrieval(doi).description)
    abstract = removeCommonWords(abstract, commonWords)
    keywords = getKeywords(AbstractRetrieval(doi, view='FULL').authkeywords)
    fields = getFields(AbstractRetrieval(doi, view='FULL').subject_areas)
    citationsCount.append(getMaximumCitationsCount(
        AbstractRetrieval(doi).citedby_count, doi))

    while True:
        try:
            query = f"INSERT INTO scopus_publications VALUES('{id}','{doi}','{year}','{title}','{abstract}','{keywords}',\
                '{fields}','{citationsCount[-1]}');"
            cursor.execute(query)
            connection.commit()
            scopusPublicationsIds[doi] = id
            uniqueDois.append(doi)
            break

        except Exception as err:
            if "Duplicate entry" not in str(err):
                print(str(err) + "\n")

            if "Data too long" in str(err):
                if "Title" in str(err):
                    titleLength += 100
                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Title VARCHAR({titleLength});"
                    cursor.execute(query)
                    connection.commit()

                elif "Abstract" in str(err):
                    abstractLength += 100
                    if abstractLength > MAX_COLUMN_SIZE:
                        print("Record rejected due to extremely large size.")
                        break
                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Abstract VARCHAR({abstractLength});"
                    cursor.execute(query)
                    connection.commit()

                elif "Keywords" in str(err):
                    keywordsLength += 100
                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Keywords VARCHAR({keywordsLength});"
                    cursor.execute(query)
                    connection.commit()

                elif "Fields" in str(err):
                    fieldsLength += 100
                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Fields VARCHAR({fieldsLength});"
                    cursor.execute(query)
                    connection.commit()

            else:
                break


# gettings authors metadata
print("Retrieving authors metadata ...")
for doi in uniqueDois:

    authors = AbstractRetrieval(doi).authors
    for author in tqdm(authors):

        authorInfo = AuthorRetrieval(author[0])
        id = str(uuid.uuid4())
        scopusId = authorInfo.identifier
        orcidId = authorInfo.orcid
        firstName = authorInfo.given_name
        lastName = authorInfo.surname
        hIndex = authorInfo.h_index
        fieldsOfStudy = getFields(authorInfo.subject_areas)
        citationsCount = authorInfo.cited_by_count
        affiliations = getAffiliations(authorInfo.affiliation_history)

        while True:
            try:
                query = f"INSERT INTO scopus_authors VALUES('{id}','{scopusId}','{orcidId}','{firstName}','{lastName}',\
                    '{fieldsOfStudy}','{affiliations}',{hIndex},{citationsCount});"
                cursor.execute(query)
                connection.commit()
                scopusAuthorsIds[scopusId] = id
                break

            except Exception as err:
                if "Duplicate entry" not in str(err):
                    print(str(err))

                if "Data too long" in str(err):
                    if "Fields_Of_Study" in str(err):
                        fieldsOfStudyLength += 100
                        query = f"ALTER TABLE scopus_authors MODIFY COLUMN Fields_Of_Study VARCHAR({fieldsOfStudyLength});"
                        cursor.execute(query)
                        connection.commit()

                    if "Affiliations" in str(err):
                        affiliationsLength += 100
                        query = f"ALTER TABLE scopus_authors MODIFY COLUMN Affiliations VARCHAR({affiliationsLength});"
                        cursor.execute(query)
                        connection.commit()

                else:
                    break

        query = f"INSERT INTO scopus_publications_authors VALUES('{scopusPublicationsIds[doi]}','{scopusAuthorsIds[scopusId]}');"
        cursor.execute(query)
        connection.commit()

# closing connection to MySQL DB
cursor.close()
connection.close()
