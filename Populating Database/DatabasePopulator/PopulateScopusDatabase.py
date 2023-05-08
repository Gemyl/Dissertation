from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval, PlumXMetrics
from requests import get
from tqdm import tqdm
from getpass import getpass
import mysql.connector as connector
import json
import uuid

# functions
def getSafeAttribute(obj, attribute, attributeType):
    try:
        if isinstance(obj, dict):
            value = obj.get(attribute)
            if((value == None) & (attributeType == "number")):
               value = 999999
            elif (obj.get(attribute) == None):
                value = "-"
        else:
            value = getattr(obj, attribute)
            if((value == None) & (attributeType == "number")):
               value = 999999
            elif (value == None):
                value = "-"

    except (AttributeError, KeyError):
        if attributeType == "number":
            value = 999999
        else:
            value = "-"
    
    return value

        
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


def getStringFromList(list):
    if list != None:
        string = ', '.join([str(i).lower() for i in list])
    else:
        string = ' '
    return string


def getColumnLength(column, table, cursor):

    try:
        query = f"SELECT MAX(LENGTH({column})) FROM {table};"
        cursor.execute(query)
        resultSet = cursor.fetchall()

        if resultSet[0][0] != None:
            return resultSet[0][0]
        else:
            return 100
        
    except:
        return 100


def applySqlSyntax(string):
    if string != None:
        return string.replace("\'", " ")
    else:
        return "-"


def removeCommonWords(abstract, commonWords):
    abstractList = abstract.split(" ")
    abstractString = " ".join(
        [word for word in abstractList if word.lower() not in commonWords])
    return abstractString


def getAffiliationsIds(affiliations):
    if affiliations != None:
        return [affil for affil in affiliations.split(";")]
    else:
        return "-"


# classes
class Publication:
    def __init__(self, publicationInfo, year, doi):
        self.id = str(uuid.uuid4())
        self.doi = doi
        self.year = year
        self.title = applySqlSyntax(getSafeAttribute(publicationInfo, 'title', 'string'))
        self.journal = applySqlSyntax(getSafeAttribute(publicationInfo, 'publicationName', 'string'))
        self.abstract = applySqlSyntax(
            Publication.getAbstract(
                getSafeAttribute(publicationInfo, 'abstract', 'string'),
                getSafeAttribute(publicationInfo, 'description', 'string')
            )
        )
        self.keywords = applySqlSyntax(Publication.getKeywords(getSafeAttribute(publicationInfo, 'authkeywords', 'string')))
        self.fields = applySqlSyntax(Publication.getFields(getSafeAttribute(publicationInfo, 'subject_areas', 'string')))
        self.citationsCount = Publication.getMaximumCitationsCount(
            getSafeAttribute(publicationInfo, 'citedby_count', 'number'),
            doi
        )
        self.authorsNumber = Publication.getAuthorsNumber(getSafeAttribute(publicationInfo, 'authors', 'list'))
        self.affiliationsNumber = Publication.getAffiliationsNumber(getSafeAttribute(publicationInfo, 'affiliation', 'list'))

    def getAbstract(abstract, description):
        if abstract != None:
            return applySqlSyntax(abstract)
        elif description != None:
            return applySqlSyntax(description)
        else:
            return "-"
        
    def getKeywords(keywords):
        if keywords != None:
            return applySqlSyntax(", ".join([keyword for keyword in keywords]))
        else:
            return "-"
    
    def getFields(fields):
        if fields != None:
            return applySqlSyntax(", ".join([field[0].lower() for field in fields]))
        else:
            return "-"
    
    def getMaximumCitationsCount(citationsCount, doi):
        maxCitations = citationsCount
        plumxCitations = PlumXMetrics(doi, id_type='doi').citation

        if plumxCitations != None:
            if maxCitations != 999999:
                plumxCitations = max([citation[1] for citation in plumxCitations])
                maxCitations = max(maxCitations, plumxCitations)
            else:
                maxCitations = max([citation[1] for citation in plumxCitations])

        return maxCitations
    
    def getAuthorsNumber(authors):
        if ((authors == "-") | (authors == None)):
            return 0
        
        return len(authors)
    
    def getAffiliationsNumber(affiliations):
        if ((affiliations == "-") | (affiliations == None)):
            return 0

        return len(affiliations)
    

class Author:
    def __init__(self,authorInfo):
        self.id = str(uuid.uuid4())
        self.scopusId = getSafeAttribute(authorInfo, 'identifier', 'string')
        self.orcidId = getSafeAttribute(authorInfo, 'orcid', 'string')
        self.firstName = applySqlSyntax(getSafeAttribute(authorInfo, 'given_name', 'string'))
        self.lastName = applySqlSyntax(getSafeAttribute(authorInfo, 'surname', 'string'))
        self.hIndex = getSafeAttribute(authorInfo, 'h_index', 'number')
        self.fieldsOfStudy = applySqlSyntax(Author.getFields(getSafeAttribute(authorInfo, 'subject_areas', 'string')))
        self.citationsCount = getSafeAttribute(authorInfo, 'cited_by_count', 'number')
        self.affiliations = applySqlSyntax(Author.getAffiliations(getSafeAttribute(authorInfo, 'affiliation_history', 'string')))

    def getAffiliations(affiliationsInput):
        if ((affiliationsInput == "-") | (affiliationsInput == None)):
            return "-"

        affilHistory = []
        for affil in affiliationsInput:
            if ((affil.preferred_name not in affilHistory) & (affil.preferred_name != None)):
                if (affil.parent == None):
                    affilHistory.append(affil.preferred_name)
                else:
                    affilHistory.append(affil.preferred_name + ' - ' + affil.parent_preferred_name)
                    affilHistory.append(affil.parent_preferred_name)

        affilHistoryStr = ', '.join(affilHistory).replace("\'", " ")
        return applySqlSyntax(affilHistoryStr)
    
    def getFields(fields):
        if (fields == "-") | (fields == None):
            return "-"
        
        return applySqlSyntax(", ".join([field[0].lower() for field in fields]))
        

class Organization:
    def __init__(self, organizationInfo):
        self.id = str(uuid.uuid4())
        self.scopusId = getSafeAttribute(organizationInfo, 'identifier', 'string')
        self.name = applySqlSyntax(getSafeAttribute(organizationInfo, 'affiliation_name', 'string'))
        self.type1, self.type2 = Organization.getAffiliationTypes(organizationInfo)
        self.address = applySqlSyntax(getSafeAttribute(organizationInfo, 'address', 'string'))
        self.city = applySqlSyntax(getSafeAttribute(organizationInfo, 'city', 'string'))
        self.country = applySqlSyntax(getSafeAttribute(organizationInfo, 'country', 'string'))

    def getAffiliationTypes(affiliationObj):
        type = getSafeAttribute(affiliationObj, 'org_type', 'string')
        name = getSafeAttribute(affiliationObj, 'affiliation_name', 'string')

        if (type == 'univ') | (type == 'coll') | \
                (len([univ for univ in university if univ in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'University - College'

        elif (type == 'sch') | \
                (len([sch for sch in school if sch in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'School'

        elif (type == 'res') | \
                (len([acad for acad in academy if acad in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'Research Institute'

        elif (type == 'gov') | \
                (len([gov for gov in government if gov in name.lower()]) > 0):
            type1 = 'Government'
            type2 = ' '

        elif (type == 'assn') | \
                (len([assn for assn in association if assn in name.lower()]) > 0):
            type1 = 'Association'
            type2 = ' '

        elif (type == 'corp') | \
                (len([bus for bus in bussiness if bus in name.lower()]) > 0):
            type1 = 'Business'
            type2 = ' '

        elif (type == 'non') | \
                (len([np for np in nonProfit if np in name.lower()]) > 0):
            type1 = 'Non-profit'
            type2 = ' '

        else:
            type1 = "Other"
            type2 = "Other"

        return type1, type2


# terminal colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

# string affiliation type identifiers
university = ['university', 'college', 'departement']
academy = ['academy', 'academic', 'academia']
school = ['school', 'faculty']
research = ['research', 'researchers']
bussiness = ['inc', 'ltd', 'corporation']
association = ['association']
nonProfit = ['non-profit']
government = ['government', 'gov', 'public', 'state', 'national', 'federal', 'federate', 'confederate', 'royal']
international = ['international']

# list of common words in order to be removed from abstracts
commonWords = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about',
               'to', 'from', 'in', 'on', 'up', 'out', 'as', 'into', 'through', 'over', 'after', 'under',
               'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'has', 'had',
               'will', 'be', 'not', 'would', 'should', 'before', 'few', 'many', 'much', 'so', 'furthermore']

# search parameters
yearPublished = '2022'
keywords = 'artificial intelligence, machine learning, learning algorithm, deep learning, pattern recognition'
fields = ['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
          'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
          'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
          'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']

# password for MySQL DB
password = getpass('Password: ')

# establishing connection to database
connection = connector.connect(host='localhost',
                               port='3306',
                               user='root',
                               password=password,
                               database="scopus",
                               auth_plugin='mysql_native_password')
cursor = connection.cursor()

# upper limit for columns size
MAX_COLUMN_SIZE = 5000

# getting columns size
doiLength = getColumnLength('DOI', 'scopus_publications', cursor)
titleLength = getColumnLength('Title', 'scopus_publications', cursor)
journalLength = getColumnLength('Title', 'scopus_publications', cursor)
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
scopusAPIKey = '&apiKey=5bc8ae0729290b95cd0bd58b92e9af41'
scopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

# declaration of lists
dois = []
filteredDois = []
filteredAuthorsScopusIds = []
citationsCount = []
authorsNumber = []
affiliationsNumber = []

# matching Scopus IDs with UUIDs
with open("IdentifiersMapping\PublicationsIds.json", "r") as f:
    publicationsScopusIds = json.load(f)

with open("IdentifiersMapping\AuthorsIds.json", "r") as f:
    scopusAuthorsIds = json.load(f)

with open("IdentifiersMapping\AffiliationsIds.json", "r") as f:
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

    try:
        publicationInfo = AbstractRetrieval(doi, view="FULL")
        publicationObj = Publication(publicationInfo, yearPublished, doi)
        publicationObj.abstract = removeCommonWords(publicationObj.abstract, commonWords)

        while True:
            try:
                query = f"INSERT INTO scopus_publications VALUES('{publicationObj.id}','{publicationObj.doi}','{publicationObj.year}','{publicationObj.title}',\
                    '{publicationObj.journal}','{publicationObj.abstract}','{publicationObj.keywords}','{publicationObj.fields}',{publicationObj.citationsCount},\
                    {publicationObj.authorsNumber},{publicationObj.affiliationsNumber});"
                cursor.execute(query)
                connection.commit()
                errorCode = 0
                break

            except Exception as err:
                if "Duplicate entry" not in str(err):
                    errorCode = 2

                    if "Data too long" in str(err):
                        if "DOI" in str(err):
                            print(doi)
                            break

                        elif "Title" in str(err):
                            titleLength += 10
                            try:
                                query = f"ALTER TABLE scopus_publications MODIFY COLUMN Title VARCHAR({titleLength});"
                                cursor.execute(query)
                                connection.commit()
                            except:
                                pass

                        elif "Journal" in str(err):
                            journalLength += 10
                            try:
                                query = f"ALTER TABLE scopus_publications MODIFY COLUMN Journal VARCHAR({journalLength});"
                                cursor.execute(query)
                                connection.commit()
                            except:
                                pass

                        elif "Abstract" in str(err):
                            abstractLength += 10
                            if abstractLength >= MAX_COLUMN_SIZE:
                                publicationObj.abstract = publicationObj.abstract[:MAX_COLUMN_SIZE]
                                abstractLength = MAX_COLUMN_SIZE
                            try:
                                query = f"ALTER TABLE scopus_publications MODIFY COLUMN Abstract VARCHAR({abstractLength});"
                                cursor.execute(query)
                                connection.commit()
                            except:
                                pass

                        elif "Keywords" in str(err):
                            keywordsLength += 10
                            try:
                                query = f"ALTER TABLE scopus_publications MODIFY COLUMN Keywords VARCHAR({keywordsLength});"
                                cursor.execute(query)
                                connection.commit()
                            except:
                                pass

                        elif "Fields" in str(err):
                            fieldsLength += 10
                            if fieldsLength >= MAX_COLUMN_SIZE:
                                publicationObj.fields = publicationObj.fields[:MAX_COLUMN_SIZE]
                                fieldsLength = MAX_COLUMN_SIZE
                            try:
                                query = f"ALTER TABLE scopus_publications MODIFY COLUMN Fields VARCHAR({fieldsLength});"
                                cursor.execute(query)
                                connection.commit()
                            except:
                                pass

                    else:
                        print(f"{BLUE}Publication Metadatata Inserting Error Info:{RESET}\n"
                              f"DOI: {doi}\n"
                              f"Error: {str(err)}")
                        break

                else:
                    errorCode = 1
                    break

        if (errorCode == 0):
            filteredDois.append(publicationObj.doi)
            publicationsScopusIds[publicationObj.doi] = publicationObj.id
            with open("IdentifiersMapping\PublicationsIds.json", "w") as f:
                json.dump(publicationsScopusIds, f, indent=4)

    except Exception as err:
        print(f"{BLUE}Publication Metadatata Retrieving Error Info:{RESET}\n"
              f"DOI: {doi}\n"
              f"Error: {str(err)}")

# getting authors metadata
print("Retrieving authors metadata ...")
for doi in tqdm(filteredDois):

    try:
        authors = AbstractRetrieval(doi).authors

        for author in authors:
            authorInfo = AuthorRetrieval(author[0])
            authorObj = Author(authorInfo)

            while True:
                try:
                    query = f"INSERT INTO scopus_authors VALUES('{authorObj.id}','{authorObj.scopusId}','{authorObj.orcidId}','{authorObj.firstName}',\
                        '{authorObj.lastName}','{authorObj.fieldsOfStudy}','{authorObj.affiliations}',{authorObj.hIndex},{authorObj.citationsCount});"
                    cursor.execute(query)
                    connection.commit()

                    filteredAuthorsScopusIds.append(authorObj.scopusId)
                    scopusAuthorsIds[authorObj.scopusId] = authorObj.id
                    with open("IdentifiersMapping\AuthorsIds.json", "w") as f:
                        json.dump(scopusAuthorsIds, f, indent=4)

                    errorCode = 0
                    break

                except Exception as err:
                    if "Duplicate entry" not in str(err):
                        errorCode = 2

                        if "Data too long" in str(err):
                            if "Fields_Of_Study" in str(err):
                                fieldsOfStudyLength += 10
                                if fieldsOfStudyLength >= MAX_COLUMN_SIZE:
                                    authorObj.fieldsOfStudy = authorObj.fieldsOfStudy[:MAX_COLUMN_SIZE]
                                    fieldsOfStudyLength = MAX_COLUMN_SIZE
                                try:
                                    query = f"ALTER TABLE scopus_authors MODIFY COLUMN Fields_Of_Study VARCHAR({fieldsOfStudyLength});"
                                    cursor.execute(query)
                                    connection.commit()
                                except:
                                    pass

                            if "Affiliations" in str(err):
                                affiliationsLength += 100
                                if affiliationsLength >= MAX_COLUMN_SIZE:
                                    authorObj.affiliations = authorObj.affiliations[:MAX_COLUMN_SIZE]
                                    affiliationsLength = MAX_COLUMN_SIZE
                                try:
                                    query = f"ALTER TABLE scopus_authors MODIFY COLUMN Affiliations VARCHAR({affiliationsLength});"
                                    cursor.execute(query)
                                    connection.commit()
                                except:
                                    pass

                        else:
                            print(f"{BLUE}Author Metadatata Inserting Error Info:{RESET}\n"
                                f"DOI: {doi}\n"
                                f"Author Scopus ID: {authorObj.scopusId}\n"
                                f"Error: {str(err)}")
                            break

                    else:
                        errorCode = 1
                        break

            if (errorCode in [0, 1]):
                query = f"INSERT INTO scopus_publications_authors VALUES('{publicationsScopusIds[doi]}','{scopusAuthorsIds[authorObj.scopusId]}');"
                cursor.execute(query)
                connection.commit()

    except Exception as err:
        print(f"{BLUE}Author Metadatata Retrieving Error Info:{RESET}\n"
            f"DOI: {doi}\n"
            f"Author Scopus ID: {authorObj.scopusId}\n"
            f"Error: {str(err)}")


# getting organizations metadata
print("Retrieving organizations metadata ...")
for doi in tqdm(filteredDois):

    try:
        authors = AbstractRetrieval(doi).authors

        for author in authors:
            affiliations = getAffiliationsIds(author[4])

            if (affiliations != "-"):
                authorId = AuthorRetrieval(author[0]).identifier

                if (authorId in filteredAuthorsScopusIds):
                    for affil in affiliations:
                        affiliationInfo = AffiliationRetrieval(int(affil), view="STANDARD")
                        organizationObj = Organization(affiliationInfo)
                        
                        while True:
                            try:
                                query = f"INSERT INTO scopus_organizations VALUES('{organizationObj.id}','{organizationObj.scopusId}','{organizationObj.name}',\
                                    '{organizationObj.type1}','{organizationObj.type2}','{organizationObj.address}','{organizationObj.city}','{organizationObj.country}');"
                                cursor.execute(query)
                                connection.commit()

                                scopusAffiliationsIds[organizationObj.scopusId] = organizationObj.id
                                with open("IdentifiersMapping\AffiliationsIds.json", "w") as f:
                                    json.dump(scopusAffiliationsIds, f, indent=4)

                                errorCode = 0
                                break

                            except Exception as err:
                                if "Duplicate entry" not in str(err):
                                    errorCode = 2

                                    if "Data too long" in str(err):
                                        if "Name" in str(err):
                                            affilNameLength += 10
                                            try:
                                                query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Name VARCHAR({affilNameLength});"
                                                cursor.execute(query)
                                                connection.commit()
                                            except:
                                                pass

                                        elif "Address" in str(err):
                                            affilAddressLength += 10
                                            try:
                                                query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Address VARCHAR({affilAddressLength});"
                                                cursor.execute(query)
                                                connection.commit()
                                            except:
                                                pass

                                        elif "City" in str(err):
                                            affilCityLength += 10
                                            try:
                                                query = f"ALTER TABLE scopus_organizations MODIFY COLUMN City VARCHAR({affilCityLength});"
                                                cursor.execute(query)
                                                connection.commit()
                                            except:
                                                pass

                                        elif "Country" in str(err):
                                            affilCountryLength += 10
                                            try:
                                                query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Country VARCHAR({affilCountryLength});"
                                                cursor.execute(query)
                                                connection.commit()
                                            except:
                                                pass

                                    else:
                                        print(f"{BLUE}Affiliation Metadatata Inserting Error Info:{RESET}\n"
                                            f"DOI: {doi}\n"
                                            f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                            f"Error: {str(err)}")
                                        break

                                else:
                                    errorCode = 1
                                    break

                        if (errorCode in [0, 1]):
                            try:
                                query = f"INSERT INTO scopus_publications_organizations VALUES('{publicationsScopusIds[doi]}', \
                                    '{scopusAffiliationsIds[organizationObj.scopusId]}');"
                                cursor.execute(query)
                                connection.commit()

                            except Exception as err:
                                if "Duplicate entry" not in str(err):
                                    print(f"{BLUE}Affiliation Metadatata Inserting Error Info:{RESET}\n"
                                        f"DOI: {doi}\n"
                                        f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                        f"Error: {str(err)}")

                            try:
                                query = f"INSERT INTO scopus_authors_organizations VALUES('{scopusAuthorsIds[authorId]}', \
                                    '{scopusAffiliationsIds[organizationObj.scopusId]}',{yearPublished});"
                                cursor.execute(query)
                                connection.commit()

                            except Exception as err:
                                if "Duplicate entry" not in str(err):
                                    print(f"{BLUE}Affiliation Metadatata Inserting Error Info:{RESET}\n"
                                        f"DOI: {doi}\n"
                                        f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                        f"Error: {str(err)}")

    except Exception as err:
        print(f"{BLUE}Affiliation Metadatata Retrieving Error Info:{RESET}\n"
            f"DOI: {doi}\n"
            f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
            f"Error: {str(err)}")

# closing connection to MySQL DB
cursor.close()
connection.close()
