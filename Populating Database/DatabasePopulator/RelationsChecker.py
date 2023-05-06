from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
import mysql.connector as connector
import json
import uuid

def replaceSingleQuote(string):
    if string != None:
        return string.replace("\'", " ")
    else:
        return "-"
    
def getFields(fields):
    if fields != None:
        return replaceSingleQuote(", ".join([field[0].lower() for field in fields]))
    else:
        return "-"
    
def getAffiliations(affiliations):
    if (affiliations == None):
        return "-"

    affilHistory = []
    for affil in affiliations:
        if ((affil.preferred_name not in affilHistory) & (affil.preferred_name != None)):
            if (affil.parent == None):
                affilHistory.append(affil.preferred_name)
            else:
                affilHistory.append(affil.preferred_name +
                                    ' - ' + affil.parent_preferred_name)
                affilHistory.append(affil.parent_preferred_name)

    affilHistoryStr = ', '.join(affilHistory).replace("\'", " ")

    return replaceSingleQuote(affilHistoryStr)

MAX_COLUMN_SIZE = 5000

publicationIds = []
dois = []
authorsPerPublication = []
flawPublicationIds = []
flawDois = []

connection = connector.connect(host='localhost',
                               port='3306',
                               user='root',
                               password='gemyl',
                               database='scopus',
                               auth_plugin='mysql_native_password')
cursor = connection.cursor()

query = "select scopus_publications.ID, scopus_publications.DOI, scopus_publications.Number_Of_Authors from \
        scopus_publications \
        inner join scopus_publications_authors on scopus_publications.ID = scopus_publications_authors.Publication_ID;"

# cursor.execute(query)
# for row in cursor:
#     publicationIds.append(row[0])
#     dois.append(row[1])
#     authorsPerPublication.append(row[2])

# sameIds = 0
# for i in range(len(publicationIds)-1):
#     if(publicationIds[i] == publicationIds[i+1]):
#         sameIds += 1
#     else:
#         sameIds += 1
#         if (sameIds != authorsPerPublication[i]):
#             flawPublicationIds.append(publicationIds[i])
#             flawDois.append(dois[i])
#         sameIds = 0

# with open("IdentifiersMapping\AuthorsIds.json","r") as f:
#     scopusAuthorsIds = json.load(f)

# with open("IdentifiersMapping\PublicationsIds.json","r") as f:
#     scopusPublicationsIds = json.load(f)

# for doi in flawDois:

#     authors = AbstractRetrieval(doi).authors

#     for author in authors:

class Author:
    def __init__(self,authorInfo) -> None:
        self.id = str(uuid.uuid4())
        self.scopusId = Author.getSafeAttribute(authorInfo, 'identifier', 'string')
        self.orcidId = Author.getSafeAttribute(authorInfo, 'orcid', 'string')
        self.firstName = Author.getSafeAttribute(authorInfo, 'given_name', 'string')
        self.lastName = Author.getSafeAttribute(authorInfo, 'surname', 'string')
        self.hIndex = Author.getSafeAttribute(authorInfo, 'h_index', 'number')
        self.fieldsOfStudy = getFields(Author.getSafeAttribute(authorInfo, 'subject_areas', 'string'))
        self.citationsCount = Author.getSafeAttribute(authorInfo, 'cited_by_count', 'number')
        self.affiliations = Author.getAffiliations(Author.getSafeAttribute(authorInfo, 'affiliation_history', 'string'))

    def getSafeAttribute(object, attribute, attributeType):
        try:
            return object[attribute]
        
        except:
            if attributeType == "number":
                return 999999
            else:
                return "-"
    
    def getAffiliations(affiliations):
        if (affiliations == "-"):
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

authorInfo = AuthorRetrieval(57190618868)
author = Author(authorInfo)
print(author)

while True:
    try:
        query = f"INSERT INTO scopus_authors VALUES('{id}','{authorScopusId}','{orcidId}','{firstName}','{lastName}',\
            '{fieldsOfStudy}','{affiliations}',{hIndex},{authorCitationsCount});"
        cursor.execute(query)
        connection.commit()

        # scopusAuthorsIds[authorScopusId] = id
        # with open("IdentifiersMapping\AuthorsIds.json", "w") as f:
        #     json.dump(scopusAuthorsIds, f, indent=4)

        errorCode = 0
        break

    except Exception as err:
        if "Duplicate entry" not in str(err):
            errorCode = 2

            if "Data too long" in str(err):
                if "Fields_Of_Study" in str(err):
                    fieldsOfStudyLength += 10
                    if fieldsOfStudyLength >= MAX_COLUMN_SIZE:
                        fieldsOfStudy = fieldsOfStudy[:MAX_COLUMN_SIZE]
                        fieldsOfStudyLength = MAX_COLUMN_SIZE
                    try:
                        query = f"ALTER TABLE scopus_authors MODIFY COLUMN Fields_Of_Study VARCHAR({fieldsOfStudyLength});"
                        cursor.execute(query)
                        connection.commit()
                    except:
                        pass

                if "Affiliations" in str(err):
                    print(affiliationsLength)
                    affiliationsLength += 100
                    if affiliationsLength >= MAX_COLUMN_SIZE:
                        affiliations = affiliations[:MAX_COLUMN_SIZE]
                        affiliationsLength = MAX_COLUMN_SIZE
                    try:
                        query = f"ALTER TABLE scopus_authors MODIFY COLUMN Affiliations VARCHAR({affiliationsLength});"
                        cursor.execute(query)
                        connection.commit()
                    except:
                        pass

            else:
                # print(f"{doi} - {authorScopusId}: {str(err)}")
                break

        else:
            errorCode = 1
            break

if (errorCode in [0, 1]):
    # query = f"INSERT INTO scopus_publications_authors VALUES('{scopusPublicationsIds[doi]}','{scopusAuthorsIds[authorScopusId]}');"
    cursor.execute(query)
    connection.commit()