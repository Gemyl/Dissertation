from Preprocessing.Methods import getColumnLength, getAffiliationsIds
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

                except Exception as pubInErr:
                    errorCodePub = 1
                    if "Duplicate entry" not in str(pubInErr):

                        if "Data too long" in str(pubInErr):
                            if "DOI" in str(pubInErr):
                                try:
                                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN DOI VARCHAR({doiLength});"
                                    cursor.execute(query)
                                    cursor.commit()
                                except:
                                    pass

                            elif "Title" in str(pubInErr):
                                titleLength += 10
                                try:
                                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Title VARCHAR({titleLength});"
                                    cursor.execute(query)
                                    connection.commit()
                                except:
                                    pass

                            elif "Journal" in str(pubInErr):
                                journalLength += 10
                                try:
                                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Journal VARCHAR({journalLength});"
                                    cursor.execute(query)
                                    connection.commit()
                                except:
                                    pass

                            elif "Abstract" in str(pubInErr):
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

                            elif "Keywords" in str(pubInErr):
                                keywordsLength += 10
                                try:
                                    query = f"ALTER TABLE scopus_publications MODIFY COLUMN Keywords VARCHAR({keywordsLength});"
                                    cursor.execute(query)
                                    connection.commit()
                                except:
                                    pass

                            elif "Fields" in str(pubInErr):
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

                            elif "Fields_Abbreviations" in str(pubInErr):
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
                            errorCodePub = 2
                            print(f"{BLUE}Publication Metadatata Inserting Error Info:{RESET}\n"
                                f"DOI: {doi}\n"
                                f"Error: {str(pubInErr)}")
                            break

                    else:
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

                            except Exception as authInErr:
                                errorCodeAut = 1
                                if "Duplicate entry" not in str(authInErr):

                                    if "Data too long" in str(authInErr):
                                        if "Fields_Of_Study" in str(authInErr):
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

                                        if "Affiliations" in str(authInErr):
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
                                        errorCodeAut = 2
                                        print(f"{BLUE}Author Inserting Error Info:{RESET}\n"
                                            f"DOI: {doi}\n"
                                            f"Error: {str(authInErr)}")
                                        break

                                else:
                                    break

                        if (errorCodeAut in [0, 1]):
                            query = f"INSERT INTO scopus_publications_authors VALUES('{publicationsScopusIds[doi]}',\
                                     '{scopusAuthorsIds[authorObj.scopusId]}');"
                            cursor.execute(query)
                            connection.commit()

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

                                                except Exception as orgInErr:
                                                    errorCodeOrg = 1
                                                    if "Duplicate entry" not in str(orgInErr):

                                                        if "Data too long" in str(orgInErr):
                                                            if "Name" in str(orgInErr):
                                                                affilNameLength += 10
                                                                try:
                                                                    query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Name VARCHAR({affilNameLength});"
                                                                    cursor.execute(query)
                                                                    connection.commit()
                                                                except:
                                                                    pass

                                                            elif "Address" in str(orgInErr):
                                                                affilAddressLength += 10
                                                                try:
                                                                    query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Address VARCHAR({affilAddressLength});"
                                                                    cursor.execute(query)
                                                                    connection.commit()
                                                                except:
                                                                    pass

                                                            elif "City" in str(orgInErr):
                                                                affilCityLength += 10
                                                                try:
                                                                    query = f"ALTER TABLE scopus_organizations MODIFY COLUMN City VARCHAR({affilCityLength});"
                                                                    cursor.execute(query)
                                                                    connection.commit()
                                                                except:
                                                                    pass

                                                            elif "Country" in str(orgInErr):
                                                                affilCountryLength += 10
                                                                try:
                                                                    query = f"ALTER TABLE scopus_organizations MODIFY COLUMN Country VARCHAR({affilCountryLength});"
                                                                    cursor.execute(query)
                                                                    connection.commit()
                                                                except:
                                                                    pass

                                                        else:
                                                            errorCodeOrg = 2
                                                            print(f"{BLUE}Organization Inserting Error Info:{RESET}\n"
                                                                f"DOI: {doi}\n"
                                                                f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                                                f"Error: {str(orgInErr)}")
                                                            break

                                                    else:
                                                        break

                                            if (errorCodeOrg in [0, 1]):
                                                try:
                                                    query = f"INSERT INTO scopus_publications_organizations VALUES('{publicationsScopusIds[doi]}', \
                                                        '{scopusAffiliationsIds[organizationObj.scopusId]}');"
                                                    cursor.execute(query)
                                                    connection.commit()

                                                except Exception as pubOrgInErr:
                                                    if "Duplicate entry" not in str(pubOrgInErr):
                                                        print(f"{BLUE}Publications - Organizations Inserting Error Info:{RESET}\n"
                                                            f"DOI: {doi}\n"
                                                            f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                                            f"Error: {str(pubOrgInErr)}")

                                                try:
                                                    query = f"INSERT INTO scopus_authors_organizations VALUES('{scopusAuthorsIds[authorId]}', \
                                                        '{scopusAffiliationsIds[organizationObj.scopusId]}',{yearPublished});"
                                                    cursor.execute(query)
                                                    connection.commit()

                                                except Exception as authOrgInErr:
                                                    if "Duplicate entry" not in str(authOrgInErr):
                                                        print(f"{BLUE}Authors - Organizations Inserting Error Info:{RESET}\n"
                                                            f"DOI: {doi}\n"
                                                            f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                                            f"Error: {str(authOrgInErr)}")

                            except Exception as orgRetErr:
                                print(f"{BLUE}Organization Retrieving Error Info:{RESET}\n"
                                    f"DOI: {doi}\n"
                                    f"Affiliation Scopus ID: {organizationObj.scopusId}\n"
                                    f"Error: {str(orgRetErr)}")
                                pass

                except Exception as authRetErr:
                    print(f"{BLUE}Author Retrieving Error Info:{RESET}\n"
                        f"DOI: {doi}\n"
                        f"Error: {str(authRetErr)}")
                    pass

        except Exception as pubRetErr:
            print(f"{BLUE}Publication Retrieving Error Info:{RESET}\n"
                f"DOI: {doi}\n"
                f"Error: {str(pubRetErr)}")
            pass