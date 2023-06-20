from Preprocessing.Methods import getColumnLength, removeCommonWords, getAffiliationsIds
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
from Entities.Classes import Publication, Author, Organization
from InputData.Items import getScopusFields
from WebScrapper.Methods import getDois
from tqdm import tqdm
import json

def extractMetadata(keywords, yearPublished, fields, booleans, apiKey, connection, cursor):
    # terminal colors
    BLUE = "\033[1;34m"
    RESET = "\033[0m"

    # upper limit for columns size
    MAX_COLUMN_SIZE = 5000

    # declaration of DOIs list
    dois = []

    # matching Scopus IDs with UUIDs
    with open("IdentifiersMapping\PublicationsIds.json", "r") as f:
        publicationsScopusIds = json.load(f)

    with open("IdentifiersMapping\AuthorsIds.json", "r") as f:
        scopusAuthorsIds = json.load(f)

    with open("IdentifiersMapping\AffiliationsIds.json", "r") as f:
        scopusAffiliationsIds = json.load(f)

    # getting columns size
    doiLength = getColumnLength('DOI', 'scopus_publications', cursor)
    titleLength = getColumnLength('Title', 'scopus_publications', cursor)
    journalLength = getColumnLength('Title', 'scopus_publications', cursor)
    abstractLength = getColumnLength('Abstract', 'scopus_publications', cursor)
    keywordsLength = getColumnLength('Keywords', 'scopus_publications', cursor)
    fieldsLength = getColumnLength('Fields', 'scopus_publications', cursor)
    fieldsAbbreviationsLength = getColumnLength('Fields_Abbreviations', 'scopus_publications', cursor)
    fieldsOfStudyLength = getColumnLength('Fields_Of_Study', 'scopus_authors', cursor)
    affiliationsLength = getColumnLength('Affiliations', 'scopus_authors', cursor)
    affilNameLength = getColumnLength('Name', 'scopus_organizations', cursor)
    affilAddressLength = getColumnLength('Address', 'scopus_piblications', cursor)
    affilCityLength = getColumnLength('City', 'scopus_organizations', cursor)
    affilCountryLength = getColumnLength('Country', 'scopus_organizations', cursor)

    scopusFields = getScopusFields(fields)

    # retrieving DOIs
    dois = getDois(keywords, yearPublished, scopusFields, booleans, apiKey)

    # getting publication metadata
    print("Getting publications metadata ...")
    for doi in tqdm(dois):

        try:
            publicationInfo = AbstractRetrieval(doi, view="FULL")
            publicationObj = Publication(publicationInfo, yearPublished, doi)

            while True:
                try:
                    query = f"INSERT INTO scopus_publications VALUES('{publicationObj.id}', \
                        '{publicationObj.doi}','{publicationObj.year}','{publicationObj.title}',\
                        '{publicationObj.journal}','{publicationObj.abstract}','{publicationObj.keywords}',\
                        '{publicationObj.fields}','{publicationObj.fieldsAbbreviations}',{publicationObj.citationsCount},\
                        {publicationObj.authorsNumber},{publicationObj.affiliationsNumber});"
                    cursor.execute(query)
                    connection.commit()
                    errorCodePub = 0
                    break

                except Exception as err:
                    if "Duplicate entry" not in str(err):
                        errorCodePub = 2

                        if "Data too long" in str(err):
                            if "DOI" in str(err):
                                try:
                                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN DOI VARCHAR({doiLength});"
                                    cursor.execute(query)
                                    cursor.commit()
                                except:
                                    pass

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

                            elif "Fields_Abbreviations" in str(err):
                                fieldsAbbreviationsLength += 10
                                if fieldsAbbreviationsLength >= MAX_COLUMN_SIZE:
                                    publicationObj.fieldsAbbreviations = publicationObj.fieldsAbbreviations[:MAX_COLUMN_SIZE]
                                    fieldsAbbreviationsLength = MAX_COLUMN_SIZE
                                try:
                                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Fields_Abbreviations VARCHAR({fieldsAbbreviationsLength});"
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
                        errorCodePub = 1
                        break

            if (errorCodePub == 0):
                publicationsScopusIds[publicationObj.doi] = publicationObj.id
                with open("IdentifiersMapping\PublicationsIds.json", "w") as f:
                    json.dump(publicationsScopusIds, f, indent=4)
                
                try:
                    authors = AbstractRetrieval(doi).authors

                    for author in authors:
                        authorInfo = AuthorRetrieval(author[0])
                        authorObj = Author(authorInfo)

                        while True:
                            try:
                                query = f"INSERT INTO scopus_authors VALUES('{authorObj.id}',\
                                    '{authorObj.scopusId}','{authorObj.orcidId}','{authorObj.firstName}',\
                                    '{authorObj.lastName}','{authorObj.fieldsOfStudy}','{authorObj.affiliations}',\
                                     {authorObj.hIndex},{authorObj.citationsCount});"
                                cursor.execute(query)
                                connection.commit()

                                scopusAuthorsIds[authorObj.scopusId] = authorObj.id
                                with open("IdentifiersMapping\AuthorsIds.json", "w") as f:
                                    json.dump(scopusAuthorsIds, f, indent=4)

                                errorCodeAut = 0
                                break

                            except Exception as err:
                                if "Duplicate entry" not in str(err):
                                    errorCodeAut = 2

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
                                        print(f"{BLUE}Author Inserting Error Info:{RESET}\n"
                                            f"DOI: {doi}\n"
                                            f"Error: {str(err)}")
                                        break

                                else:
                                    errorCodeAut = 1
                                    break

                        if (errorCodeAut in [0, 1]):
                            query = f"INSERT INTO scopus_publications_authors VALUES('{publicationsScopusIds[doi]}',\
                                     '{scopusAuthorsIds[authorObj.scopusId]}');"
                            cursor.execute(query)
                            connection.commit()

                            if (errorCodeAut == 0):
                                try:
                                    authors = AbstractRetrieval(doi).authors

                                    for author in authors:
                                        authorId = str(AuthorRetrieval(author[0]).identifier)
                                        affiliations = getAffiliationsIds(author[4])

                                        if ((affiliations != "-") & (authorId == authorObj.scopusId)):
                                            for affil in affiliations:
                                                affiliationInfo = AffiliationRetrieval(int(affil), view="STANDARD")
                                                organizationObj = Organization(affiliationInfo)
                                                
                                                while True:
                                                    try:
                                                        query = f"INSERT INTO scopus_organizations VALUES('{organizationObj.id}',\
                                                                '{organizationObj.scopusId}','{organizationObj.name}','{organizationObj.type1}',\
                                                                '{organizationObj.type2}','{organizationObj.address}','{organizationObj.city}',\
                                                                '{organizationObj.country}');"
                                                        cursor.execute(query)
                                                        connection.commit()

                                                        scopusAffiliationsIds[organizationObj.scopusId] = organizationObj.id
                                                        with open("IdentifiersMapping\AffiliationsIds.json", "w") as f:
                                                            json.dump(scopusAffiliationsIds, f, indent=4)

                                                        errorCodeOrg = 0
                                                        break

                                                    except Exception as err:
                                                        if "Duplicate entry" not in str(err):
                                                            errorCodeOrg = 2

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
                                                                print(f"{BLUE}Organization Inserting Error Info:{RESET}\n"
                                                                    f"DOI: {doi}\n"
                                                                    f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                                                    f"Error: {str(err)}")
                                                                break

                                                        else:
                                                            errorCodeOrg = 1
                                                            break

                                                if (errorCodeOrg in [0, 1]):
                                                    try:
                                                        query = f"INSERT INTO scopus_publications_organizations VALUES('{publicationsScopusIds[doi]}', \
                                                            '{scopusAffiliationsIds[organizationObj.scopusId]}');"
                                                        cursor.execute(query)
                                                        connection.commit()

                                                    except Exception as err:
                                                        if "Duplicate entry" not in str(err):
                                                            print(f"{BLUE}Publications - Organizations Inserting Error Info:{RESET}\n"
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
                                                            print(f"{BLUE}Authors - Organizations Inserting Error Info:{RESET}\n"
                                                                f"DOI: {doi}\n"
                                                                f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                                                f"Error: {str(err)}")

                                except Exception as err:
                                    print(f"{BLUE}Organization Retrieving Error Info:{RESET}\n"
                                        f"DOI: {doi}\n"
                                        f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                        f"Error: {str(err)}")

                except Exception as err:
                    print(f"{BLUE}Author Retrieving Error Info:{RESET}\n"
                        f"DOI: {doi}\n"
                        f"Error: {str(err)}")

        except Exception as err:
            print(f"{BLUE}Publication Retrieving Error Info:{RESET}\n"
                f"DOI: {doi}\n"
                f"Error: {str(err)}")