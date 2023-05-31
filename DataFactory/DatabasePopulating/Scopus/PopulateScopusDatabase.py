from Preprocessing.Methods import getColumnLength, removeCommonWords, getAffiliationsIds
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
from Entities.Classes import Publication, Author, Organization
from InputData.Items import getKeywords, getYear, getFields, getCommonWords
from DuplicatesDetection.PublicationsDuplicates import detectPublicationsDuplicates
from DuplicatesDetection.AuthorsDuplicates import detectAuthorsDuplicates
from DuplicatesDetection.OrganizationsDuplicates import detectOrganizationsDuplicates
from ConnectToMySQL.Connector import connect
from WebScrapper.Methods import getMetadata
from tqdm import tqdm
import json

# terminal colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

# upper limit for columns size
MAX_COLUMN_SIZE = 5000

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

# establishing connection to database
connection, cursor = connect()

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

# input data
keywords = getKeywords()
yearPublished = getYear()
fields = getFields()
commonWords = getCommonWords()

# retrieving DOIs
dois = getMetadata(keywords, yearPublished, fields)

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
            f"Error: {str(err)}")


# getting organizations metadata
print("Retrieving organizations metadata ...")
for doi in tqdm(filteredDois):

    try:
        authors = AbstractRetrieval(doi).authors

        for author in authors:
            affiliations = getAffiliationsIds(author[4])

            if (affiliations != "-"):
                authorId = str(AuthorRetrieval(author[0]).identifier)

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
        
#detecting and storing duplicates
detectPublicationsDuplicates(connection, cursor)
detectAuthorsDuplicates(connection, cursor)
detectOrganizationsDuplicates(connection, cursor)

# closing connection to MySQL DB
cursor.close()
connection.close()
