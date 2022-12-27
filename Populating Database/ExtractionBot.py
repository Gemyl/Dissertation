from MySQLpackage import connect_to_MySQL, insert_publications, insert_authors, insert_organizations, \
     insert_publications_and_authors, insert_publications_and_organizations, commit_and_close
from DataRetrieving import get_DOIs, papers_data, authors_data, orgs_data, \
     papers_and_authors, papers_and_orgs
from getpass import getpass

# parameters given by user
keywords = str(input('Keywords: '))
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')
password = getpass('Password: ')

# finding DOIs of related publications
DOIs = get_DOIs(keywords, yearsRange, subjects)

# retrieving data of papers, authors and organizations
DOI, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount \
     = papers_data(DOIs, keywords)

authorID, eid, orcid, name, hIndex, subjectAreas, itemCitations, authorsCitations, \
    documentsCount = authors_data(DOIs)

orgID, orgEID, orgName, orgType, orgAddress, orgPostalCode, orgCity, orgState, \
     orgCountry =  orgs_data(DOIs)

# retrieving identifiers to form collaboration table between authors and organizations
DOIPapersAuthors, IDAuthorsPapers = papers_and_authors(DOIs)
DOIPapersOrgs, IDOrgsPapers = papers_and_orgs(DOIs)


# inserting data to MySQL database
# openning connection
connection, cursor = connect_to_MySQL(password)

# data insertion
insert_publications(cursor, DOI, year, journal, authorshipKeywords, userKeywords, 
     subjects, title, citationsCount)
insert_authors(cursor, authorID, eid, orcid, name, hIndex, subjectAreas, itemCitations, 
     authorsCitations, documentsCount)
insert_organizations(cursor, orgID, orgEID, orgName, orgType, orgAddress, orgPostalCode,
     orgCity, orgState, orgCountry)
insert_publications_and_authors(cursor, DOIPapersAuthors, IDAuthorsPapers)
insert_publications_and_organizations(cursor, DOIPapersOrgs, IDOrgsPapers)

# committing changes and closing connection
commit_and_close(connection, cursor)