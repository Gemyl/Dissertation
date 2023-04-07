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
            keywordsList = keywordsList + '{' + keywords[i] + '} ' + 'AND '

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


# search parameters
keywords = 'artificial intelligence, machine learning'
yearsRange = '2022'
fields = ['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
          'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
          'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
          'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']

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

# query parameters
count = '&count=25'
term1 = '( {python} )'
term2 = buildKeywordsQuery(keywords)
terms = f'( {term1} AND {term2} )'
scope = 'TITLE-ABS-KEY'
view = '&view=standard'
sort = '&sort=citedby_count'
date = '&date=' + str(yearsRange)
scopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'
scopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

for field in tqdm(fields):

    startIndex = 0
    while True:
        start = f"&start={startIndex}"
        currentField = f"&subj={field}"
        query = 'query=' + scope + terms + date + start + \
            count + sort + currentField + scopusAPIKey + view
        url = scopusBaseUrl + query

        req = get(url)
        if req.status_code == 200:
            content = json.loads(req.content)['search-results']
            totalResults = int(content['opensearch:totalResults'])
            startIndex = int(content['opensearch:startIndex'])
            metadata = content['entry']
            with open("metadata.json", "w") as f:
                json.dump(metadata, f, indent=4)
        else:
            Error = json.loads(req.content)['service-error']['status']
            print(req.status_code, Error['statusText'])

        remainingData = totalResults - startIndex - len(metadata)

        if remainingData > 0:
            startIndex += 25
        else:
            break
