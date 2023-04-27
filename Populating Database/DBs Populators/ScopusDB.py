from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval, PlumXMetrics
from requests import get
from tqdm import tqdm
from getpass import getpass
import mysql.connector as connector
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

# get columns length
def getColumnLength(column, table, cursor):

    try:
        query = f"SELECT MAX(LENGTH({column})) FROM {table};"
        cursor.execute(query)
        resultSet = cursor.fetchall()

        if resultSet[0][0] != None:
            return resultSet[0][0]
        else:
            return 500

    except:
        return 500


# replace "'" with "\'" for valid SQL syntax
def replaceSingleQuote(string):

    if string != None:
        return string.replace("\'", " ")
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

    if(affiliations == None):
        return "-"
    
    affilHistory = []
    for affil in affiliations:
        if ((affil.preferred_name not in affilHistory) & (affil.preferred_name != None)):
            if (affil.parent == None):
                affilHistory.append(affil.preferred_name)
            else:
                affilHistory.append(affil.preferred_name + ' - ' + affil.parent_preferred_name)
                affilHistory.append(affil.parent_preferred_name)

    affilHistoryStr = ', '.join(affilHistory).replace("\'", " ")

    return replaceSingleQuote(affilHistoryStr)


def getAffiliationsIds(affiliations):

    if affiliations != None:
        return [affil for affil in affiliations.split(";")]
    else:
        return "-"


def getAffiliationTypes(affiliationObj):

    if (affiliationObj.org_type == 'univ') | (affiliationObj.org_type == 'coll') | \
            (len([univ for univ in university if univ in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Academic'
        type2 = 'University - College'

    elif (affiliationObj.org_type == 'sch') | \
            (len([sch for sch in school if sch in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Academic'
        type2 = 'School'

    elif (affiliationObj.org_type == 'res') | \
            (len([acad for acad in academy if acad in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Academic'
        type2 = 'Research Institute'

    elif (affiliationObj.org_type == 'gov') | \
            (len([gov for gov in government if gov in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Government'
        type2 = ' '

    elif (affiliationObj.org_type == 'assn') | \
            (len([assn for assn in association if assn in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Association'
        type2 = ' '

    elif (affiliationObj.org_type == 'corp') | \
            (len([bus for bus in bussiness if bus in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Business'
        type2 = ' '

    elif (affiliationObj.org_type == 'non') | \
            (len([np for np in nonProfit if np in affiliationObj.affiliation_name.lower()]) > 0):
        type1 = 'Non-profit'
        type2 = ' '

    else:
        type1 = "Other"
        type2 = "Other"

    return type1, type2


# count publication's affiliations
def countAffiliations(affiliations):

    if (affiliations == None):
        return 0
    
    return len(affiliations)


# string affiliation type identifiers
university = ['univ', 'university', 'universiti', 'universidade', 'universidad', 'college',
              'universität', 'departement', 'dept', 'uniwersytet', 'dipartimento']
academy = ['academy', 'academic', 'academia']
school = ['school', 'faculty']
research = ['research', 'researchers', 'institut']
bussiness = ['inc', 'ltd']
association = ['association']
nonProfit = ['non-profit']
government = ['government', 'gov', 'public', 'state', 'national',
              'federal', 'federate', 'confederate', 'royal']
international = ['international']

# list of common words in order to be removed from abstracts
commonWords = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about',
               'to', 'from', 'in', 'on', 'up', 'out', 'as', 'into', 'through', 'over', 'after', 'under',
               'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'has', 'had',
               'will', 'be', 'not', 'would', 'should', 'before', 'few', 'many', 'much', 'so', 'furthermore']


# search parameters
keywords = 'ai'
yearPublished = '2022'
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

# upper limit for columns size
MAX_COLUMN_SIZE = 1500

# getting columns size
titleLength = getColumnLength('Title', 'scopus_publications', cursor)
abstractLength = getColumnLength('Abstract', 'scopus_publications', cursor)
keywordsLength = getColumnLength('Keywords', 'scopus_publications', cursor)
fieldsLength = getColumnLength('Fields', 'scopus_publications', cursor)
fieldsOfStudyLength = getColumnLength('Fields_Of_Study', 'scopus_authors', cursor)
affiliationsLength = getColumnLength('Affiliations', 'scopus_authors', cursor)
affilNameLength = getColumnLength('Name', 'scopus_organizations', cursor)
affilAddressLength = getColumnLength('Address', 'scopus_piblications', cursor)
affilCityLength = getColumnLength('City', 'scopus_organizations', cursor)
affilCountryLength = getColumnLength('Country', 'scopus_organizations', cursor)

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

# declaration of lists
dois = []
uniqueDois = []
uniqueAuthorsScopusIds = []
citationsCount = []
authorsNumber = []
affiliationsNumber = []

# matching Scopus IDs with UUIDs
with open("Populating Database\DBs Populators\IdsMaps\PublicationsIds.json","r") as f:
    scopusPublicationsIds = json.load(f)

with open("Populating Database\DBs Populators\IdsMaps\AuthorsIds.json","r") as f:
    scopusAuthorsIds = json.load(f)

with open("Populating Database\DBs Populators\IdsMaps\AffiliationsIds.json","r") as f:
    scopusAffiliationsIds = json.load(f)

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

# getting publication metadata
print("Getting publications metadata ...")
for doi in tqdm(dois):

    publicationInfo = AbstractRetrieval(doi, view="FULL")

    id = str(uuid.uuid4())
    year = yearPublished
    title = replaceSingleQuote(publicationInfo.title)
    abstract = getAbstract(publicationInfo.abstract, publicationInfo.description)
    abstract = removeCommonWords(abstract, commonWords)
    keywords = getKeywords(publicationInfo.authkeywords)
    fields = getFields(publicationInfo.subject_areas)
    citationsCount = getMaximumCitationsCount(publicationInfo.citedby_count, doi)
    authorsNumber = len(publicationInfo.authors)
    affiliationsNumber = countAffiliations(publicationInfo.affiliation)

    while True:
        try:
            query = f"INSERT INTO scopus_publications VALUES('{id}','{doi}','{year}','{title}','{abstract}','{keywords}',\
                '{fields}',{citationsCount},{authorsNumber},{affiliationsNumber});"
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
                        try:
                            query = f"ALTER TABLE scopus_publications MODIFY COLUMN Title VARCHAR({titleLength});"
                            cursor.execute(query)
                            connection.commit()
                        except:
                            pass

                    elif "Abstract" in str(err):
                        abstractLength += 100
                        if abstractLength >= MAX_COLUMN_SIZE:
                            abstract = abstract[:1500]
                            abstractLength = 1500
                        try:
                            query = f"ALTER TABLE scopus_publications MODIFY COLUMN Abstract VARCHAR({abstractLength});"
                            cursor.execute(query)
                            connection.commit()
                        except:
                            pass

                    elif "Keywords" in str(err):
                        keywordsLength += 100
                        try:
                            query = f"ALTER TABLE scopus_publications MODIFY COLUMN Keywords VARCHAR({keywordsLength});"
                            cursor.execute(query)
                            connection.commit()
                        except:
                            pass

                    elif "Fields" in str(err):
                        fieldsLength += 100
                        try:
                            query = f"ALTER TABLE scopus_publications MODIFY COLUMN Fields VARCHAR({fieldsLength});"
                            cursor.execute(query)
                            connection.commit()
                        except:
                            pass
            else:
                break


# getting authors metadata
print("Retrieving authors metadata ...")
for doi in tqdm(uniqueDois):

    authors = AbstractRetrieval(doi).authors

    for author in authors:

        authorInfo = AuthorRetrieval(author[0])
        id = str(uuid.uuid4())
        scopusId = authorInfo.identifier
        orcidId = authorInfo.orcid
        firstName = replaceSingleQuote(authorInfo.given_name)
        lastName = replaceSingleQuote(authorInfo.surname)
        hIndex = authorInfo.h_index
        fieldsOfStudy = replaceSingleQuote(getFields(authorInfo.subject_areas))
        authorCitationsCount = authorInfo.cited_by_count
        affiliations = replaceSingleQuote(getAffiliations(authorInfo.affiliation_history))

        while True:
            try:
                query = f"INSERT INTO scopus_authors VALUES('{id}','{scopusId}','{orcidId}','{firstName}','{lastName}',\
                    '{fieldsOfStudy}','{affiliations}',{hIndex},{authorCitationsCount});"
                cursor.execute(query)
                connection.commit()
                scopusAuthorsIds[scopusId] = id
                uniqueAuthorsScopusIds.append(scopusId)
                break

            except Exception as err:
                if "Duplicate entry" not in str(err):
                    print(str(err))

                if "Data too long" in str(err):
                    if "Fields_Of_Study" in str(err):
                        fieldsOfStudyLength += 100
                        try:
                            query = f"ALTER TABLE scopus_authors MODIFY COLUMN Fields_Of_Study VARCHAR({fieldsOfStudyLength});"
                            cursor.execute(query)
                            connection.commit()
                        except:
                            pass

                    if "Affiliations" in str(err):
                        affiliationsLength += 100
                        if affiliationsLength >= MAX_COLUMN_SIZE:
                            affiliations = affiliations[:1500]
                            affiliationsLength = 1500
                        try:
                            query = f"ALTER TABLE scopus_authors MODIFY COLUMN Affiliations VARCHAR({affiliationsLength});"
                            cursor.execute(query)
                            connection.commit()
                        except:
                            pass
                else:
                    break

        query = f"INSERT INTO scopus_publications_authors VALUES('{scopusPublicationsIds[doi]}','{scopusAuthorsIds[scopusId]}');"
        cursor.execute(query)
        connection.commit()


# getting organizations metadata
print("Retrieving organizations metadata ...")
for doi in tqdm(uniqueDois):

    authors = AbstractRetrieval(doi).authors

    for author in authors:

        affiliations = getAffiliationsIds(author[4])
        if (affiliations != "-") & (author[0] in uniqueAuthorsScopusIds):
            for affil in affiliations:

                affilInfo = AffiliationRetrieval(affil)

                id = str(uuid.uuid4())
                scopusId = affilInfo.identifier
                name = replaceSingleQuote(affilInfo.affiliation_name)
                type1, type2 = getAffiliationTypes(affilInfo)
                address = replaceSingleQuote(affilInfo.address)
                city = replaceSingleQuote(affilInfo.city)
                country = replaceSingleQuote(affilInfo.country)

                while True:
                    try:
                        query = f"INSERT INTO scopus_organizations VALUES('{id}','{scopusId}','{name}','{type1}',\
                            '{type2}','{address}','{city}','{country}');"
                        cursor.execute(query)
                        connection.commit()
                        scopusAffiliationsIds[scopusId] = id
                        break

                    except Exception as err:
                        if "Duplicate entry" not in str(err):
                            print(str(err))

                            if "Data too long" in str(err):
                                if "Name" in str(err):
                                    affilNameLength += 100
                                    try:
                                        query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Name VARCHAR({affilNameLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                elif "Address" in str(err):
                                    affilAddressLength += 100
                                    try:
                                        query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Address VARCHAR({affilAddressLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                elif "City" in str(err):
                                    affilCityLength += 100
                                    try:
                                        query = f"ALTER TABLE scopus_organizations MODIFY COLUMN City VARCHAR({affilCityLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                elif "Name" in str(err):
                                    affilCountryLength += 100
                                    try:
                                        query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Country VARCHAR({affilCountryLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass
                        else:
                            break

                query = f"INSERT INTO scopus_publications_organizations VALUES('{scopusPublicationsIds[doi]}', \
                    '{scopusAffiliationsIds[scopusId]}');"
                cursor.execute(query)
                connection.commit()

                query = f"INSERT INTO scopus_authors_organizations VALUES('{scopusAuthorsIds[author[0]]}', \
                    '{scopusAffiliationsIds[scopusId]}',{yearPublished});"
                cursor.execute(query)
                connection.commit()


# updating ids maps
with open("Populating Database\DBs Populators\IdsMaps\PublicationsIds.json","w") as f:
    json.dump(scopusPublicationsIds, f, indent=4)

with open("Populating Database\DBs Populators\IdsMaps\AuthorsIds.json","w") as f:
    json.dump(scopusAuthorsIds, f, indent=4)

with open("Populating Database\DBs Populators\IdsMaps\AffiliationsIds.json","w") as f:
    json.dump(scopusAffiliationsIds, f, indent=4)

# closing connection to MySQL DB
cursor.close()
connection.close()
