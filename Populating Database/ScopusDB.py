
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval, PlumXMetrics
from math import radians, sin, cos, sqrt, atan2
from textformating import list_to_string
from geopy.geocoders import Nominatim
import mysql.connector as connector
from itertools import combinations
from statistics import mean
from requests import get
from tqdm import tqdm
from getpass import getpass
import json
import uuid


# ************ FUNCTIONS ************ #
def list_to_string(list):

    if list != None:
        string = ', '.join([str(i).lower() for i in list])
    else:
        string = ' '

    return string


def format_keywords(keywords):
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


def distance(lat1, lon1, lat2, lon2):
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


def get_DOIs(keywords, yearsRange, subjects):

    DOIs = []
    count = '&count=25'
    term1 = '( {python} )'
    term2 = format_keywords(keywords)
    terms = '( {} AND {} )'.format(term1, term2)
    scope = 'TITLE-ABS-KEY'
    view = '&view=standard'
    sort = '&sort=citedby_count'
    date = '&date=' + str(yearsRange)
    scopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'
    scopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

    for sub in tqdm(subjects):

        # startIndex is used to summarize all the previous DOIs
        # that have been retrieved for a given subject
        startIndex = 0

        while True:

            start = '&start={}'.format(startIndex)
            subj = '&subj={}'.format(sub)

            query = 'query=' + scope + terms + date + start + \
                count + sort + subj + scopusAPIKey + view
            url = scopusBaseUrl + query

            # sending request to Scopus
            req = get(url)
            if req.status_code == 200:
                content = json.loads(req.content)['search-results']
                totalResults = int(content['opensearch:totalResults'])
                startIndex = int(content['opensearch:startIndex'])
                metadata = content['entry']
            else:
                Error = json.loads(req.content)['service-error']['status']
                print(req.status_code, Error['statusText'])

            for metadataIndex in metadata:
                try:
                    TempDOI = metadataIndex['prism:doi']
                    DOIs.append(str(TempDOI))
                except:
                    continue

            # 'totalResults' is the number of all items that search has been resulted in
            # 'startIndex' is the number of items whose data have been already obtained
            # the length of 'metadata' is the number of items whose data are going to be extracted
            Remain = totalResults - startIndex - len(metadata)

            if Remain > 0:
                startIndex += 25
            else:
                break

    return DOIs


# ************* POPULATING DATABASE ************* #
# parameters given by user
keywords = 'AI'
yearsRange = '2022'
subjects = ['SOCI']
password = getpass('Password: ')


# finding DOIs of related publications
print('Retrieving DOIs:')
DOIs = get_DOIs(keywords, yearsRange, subjects)


# establishing connection to database
connection = connector.connect(host='localhost',
                               port='3306',
                               user='root',
                               password=password,
                               database='scopus',
                               auth_plugin='mysql_native_password')

cursor = connection.cursor()


# **************** PUBLICATIONS METADATA **************** #
print('\nRetrieving papers data:')

citationsCount = []

for doi in tqdm(DOIs):

    paperInfo = AbstractRetrieval(doi, view='FULL')

    year = yearsRange
    userKeywords = keywords
    title = str(paperInfo.title).replace('\'', '\\' + '\'')
    journal = str(paperInfo.publisher)
    authorsKeywords = list_to_string(paperInfo.authkeywords)
    subjects = ', '.join(str(sub[0]).lower()
                         for sub in paperInfo.subject_areas)

    # paper'smaximum number of citations
    maxCitations = paperInfo.citedby_count
    plumxCitations = PlumXMetrics(doi, id_type='doi').citation

    if plumxCitations != None:

        plumxCitations = max([citation[1] for citation in plumxCitations])
        maxCitations = max(maxCitations, plumxCitations)

    citationsCount.append(str(maxCitations))

    try:
        query = 'INSERT INTO publications VALUES (\'' + str(doi) + '\', ' + year + ', \'' + title + '\', \'' + \
            authorsKeywords + '\', \'' + subjects + '\', \'' + \
                citationsCount[len(citationsCount)-1] + '\');'

        cursor.execute(query)
        connection.commit()

    except:
        continue


# ******************** AUTHORS METADATA ******************** #
print('\nRetrieving authors data:')
AuthorsID = {}
for doi in tqdm(DOIs):

    # getting a paper's authors
    authors = AbstractRetrieval(doi).authors

    # in this loop every author is accessed
    for author in authors:
        # getting all the available information for each author
        authorInfo = AuthorRetrieval(author[0])

        # checking if an author has been already accesed during this search
        identifier = str(uuid.uuid4())
        authorScopusID = str(authorInfo.identifier)
        orcidId = str(authorInfo.orcid)
        firstName = str(authorInfo.given_name)
        lastName = str(authorInfo.surname)
        indexedName = str(authorInfo.indexed_name)
        subjectedAreas = ', '.join(str(sub[0]).lower()
                                   for sub in authorInfo.subject_areas)
        hIndex = str(authorInfo.h_index)
        itemCitations = str(authorInfo.citation_count)
        authorsCitations = str(authorInfo.cited_by_count)
        documentsCount = str(authorInfo.document_count)

        AuthorsID[authorScopusID] = identifier

        query = 'INSERT INTO authors VALUES (\'' + identifier + \
            '\', \'' + authorScopusID + '\', \'' + orcidId + '\', \'' \
            + firstName + '\', \'' + lastName + '\', ' + hIndex + ', \'' + \
            subjectedAreas + '\', ' + itemCitations + ');'

        cursor.execute(query)
        connection.commit()


# **************** ORGANIZATIONS METADATA **************** #
print('\nRetrieving organizations data:')
orgID = []
cityTemp = []
cityDist = []
type1Temp = []
type2Temp = []
type1Dist = []
type2Dist = []

orgsID = {}

for doi in tqdm(DOIs):

    paperOrgs = AbstractRetrieval(doi).affiliation

    for org in paperOrgs:

        orgInfo = AffiliationRetrieval(org[0])
        identifier = str(uuid.uuid4())
        orgScopusID = str(orgInfo.identifier)
        name = str(org[1])
        city = str(orgInfo.city)
        state = str(orgInfo.state)
        country = str(orgInfo.country)
        address = str(orgInfo.address)
        postalCode = str(orgInfo.postal_code)

        if orgInfo.org_type == 'univ':
            type1 = 'Academic'
            type2 = 'University - College'
        elif orgInfo.org_type == 'coll':
            type1 = 'Academic'
            type2 = 'University - College'
        elif orgInfo.org_type == 'sch':
            type1 = 'Academic'
            type2 = 'School'
        elif orgInfo.org_type == 'res':
            type1 = 'Academic'
            type2 = 'Research Institute'
        elif orgInfo.org_type == 'gov':
            type1 = 'Government'
            type2 = ' '
        elif orgInfo.org_type == 'assn':
            type1 = 'Association'
            type2 = ' '
        elif orgInfo.org_type == 'corp':
            type1 = 'Business'
            type2 = ' '
        elif orgInfo.org_type == 'non':
            type1 = 'Non-profit'
            type2 = ' '
        elif ('university' in name.lower()) | ('universiti' in name.lower()) | \
            ('universidade' in name.lower()) | ('universidad' in name.lower()) | \
            ('college' in name.lower()) | ('universität' in name.lower()) | \
            ('department' in name.lower()) | ('dept.' in name.lower()) | \
                ('uniwersytet' in name.lower()) | ('dipartimento' in name.lower()):
            type1 = 'Academic'
            type2 = 'University - College'
        elif ('academy' in name.lower()) | ('academic' in name.lower()):
            type1 = 'Academic'
            type2 = 'Academy'
        elif ('school' in name.lower()) | ('faculty' in name.lower()):
            type1 = 'Academic'
            type2 = 'School'
        elif ('research' in name.lower()) | ('researchers' in name.lower()):
            type1 = 'Academic'
            type2 = 'Research Institute'
        elif ('inc.' in name.lower()) | ('inc' in name.lower()) | \
                ('ltd.' in name.lower()) | ('ltd' in name.lower()):
            type1 = 'Business'
            type2 = ' '
        elif ('association' in name.lower()):
            type1 = 'Association'
            type2 = ' '
        elif ('non-profit' in name.lower()):
            type1 = 'Non-profit'
            type2 = ' '
        elif ('government' in name.lower()) | ('public' in name.lower()) | \
            ('state' in name.lower()) | ('national' in name.lower()) | \
            ('federal' in name.lower()) | ('royal' in name.lower()) | \
                ('federate' in name.lower()) | ('confederate' in name.lower()):
            type1 = 'Government'
            type2 = ' '
        elif ('international' in name.lower()) | ('intergovernmental' in name.lower()):
            type1 = 'International'
            type2 = ' '
        else:
            type1 = 'Other'
            type2 = ' '

        orgsID[orgScopusID] = identifier

        type1Temp.append(type1)
        type2Temp.append(type2)
        cityTemp.append(city)

        try:
            query = 'INSERT INTO organizations VALUES (\'' + identifier + '\', \'' + orgScopusID + '\', \'' \
                + name + '\', \'' + type1 + '\', \'' + type2 + '\', \'' + address + '\', \'' + city + '\', \'' \
                + country + '\');'

            cursor.execute(query)
            connection.commit()

        except:
            continue

    type1Dist.append(type1Temp)
    type2Dist.append(type2Temp)
    cityDist.append(cityTemp)

    cityTemp = []
    type1Temp = []
    type2Temp = []
    parentOrgs = []


# ************** PUBLICATIONS & AUTHORS ************** #
print('\nMatching papers with authors:')
for doi in tqdm(DOIs):

    authors = AbstractRetrieval(doi).authors

    for author in authors:

        authorID = AuthorsID[str(AuthorRetrieval(author[0]).identifier)]

        try:
            query = 'INSERT INTO publications_authors VALUES (\'' + \
                    doi + '\', \'' + authorID + '\');'

            cursor.execute(query)
            connection.commit()

        except:
            continue


# ***************** PUBLICATIONS & ORGANIZATIONS ***************** #
print('\nMatching papers with organizations:')
for doi in tqdm(DOIs):

    pubOrgs = [str(org[0])
               for org in AbstractRetrieval(doi).affiliation]

    authors = AbstractRetrieval(doi).authors

    for org in pubOrgs:

        orgID = orgsID[org]

        try:
            query = 'INSERT INTO publications_organizations VALUES (\'' + doi + '\', \'' + \
                orgID + '\');'

            cursor.execute(query)
            connection.commit()

        except:
            continue

    tempOrgs = []


# **************** AUTHORS & ORGANIZATIONS **************** #
print('\nMatching authors with organizations:')
for doi in tqdm(DOIs):

    for author in AbstractRetrieval(doi).authors:

        authorID = AuthorsID[str(AuthorRetrieval(author[0]).identifier)]

        if author[4] != None:

            affil = author[4].split(';')

            for org in affil:

                orgID = orgsID[org]

                try:
                    query = 'INSERT INTO authors_organizations VALUES (\'' + \
                        authorID + '\', \'' + orgID + '\');'

                    cursor.execute(query)
                    connection.commit()

                except:
                    continue


# ******************** DISTANCES ******************** #
print('\nCalculating geographical distances per publication:')
distTemp = []
distances = []
cityCoord = []

orgTypeDict = {'Academic': 0,
               'Government': 1,
               'Business': 2,
               'International': 3,
               'Non-profit': 4,
               'Association': 5}

orgDistMap = [[1, 3, 5, 4, 3],
              [3, 1, 5, 3, 4],
              [5, 5, 1, 5, 5],
              [4, 3, 5, 1, 4],
              [3, 4, 5, 4, 1]]

for k in tqdm(range(len(DOIs))):

    try:
        geolocator = Nominatim(user_agent='PersonalProject')
        if len(cityDist[k]) == 1:
            minGeoDist = str(0)
            maxGeoDist = str(0)
            avgGeoDist = str(0)
            minOrgDist = str(1)
            maxOrgDist = str(1)
            avgOrgDist = str(1)

        else:
            for city in cityDist[k]:
                location = geolocator.geocode(city)
                cityCoord.append((location.latitude, location.longitude))

            combos = list(combinations(cityCoord, 2))

            for combo in combos:
                distances.append(
                    distance(combo[0][0], combo[0][1], combo[1][0], combo[1][1]))

            minGeoDist = str(min(distances))
            maxGeoDist = str(max(distances))
            avgGeoDist = str(mean(distances))

            if 'Other' not in type1Dist[k]:
                for i in range(len(type1Dist[k])-1):
                    for j in range(i+1, len(type1Dist[k])):
                        index1 = orgTypeDict[type1Dist[k][i]]
                        index2 = orgTypeDict[type1Dist[k][j]]
                        dist = orgDistMap[index1][index2]
                        distTemp.append(dist)

                minOrgDist = str(min(distTemp))
                maxOrgDist = str(max(distTemp))
                avgOrgDist = str(mean(distTemp))

            else:
                minOrgDist = str(0)
                maxOrgDist = str(0)
                avgOrgDist = str(0)

        query = 'INSERT INTO distances VALUES (\'' + DOIs[k] + '\', ' + citationsCount[k] + ', ' \
            + minGeoDist + ', ' + maxGeoDist + ', ' + avgGeoDist + ', ' + minOrgDist + ', ' + \
            maxOrgDist + ', ' + avgOrgDist + ');'

        cursor.execute(query)
        connection.commit()

        distTemp = []
        distances = []
        cityCoord = []

    except:
        continue


# *** CLOSING CONNECTION *** #
cursor.close()
connection.close()
