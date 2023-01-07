from MySQLpackage import connect_to_MySQL, insert_publications, insert_authors, insert_organizations, \
     insert_publications_and_authors, insert_publications_and_organizations, commit_and_close, insert_authors_and_publications, \
     instert_cultural_distances
from DataRetrieving import get_DOIs, papers_data, authors_data, orgs_data, papers_and_authors, papers_and_orgs, \
     authors_and_organizations, cultural_distances
from getpass import getpass

# parameters given by user
keywords = str(input('Keywords: '))
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')
password = getpass('Password: ')

# finding DOIs of related publications
DOIs = get_DOIs(keywords, yearsRange, subjects)
# establishing connection with database
connection, cursor, error = connect_to_MySQL(password)

# retrieving and inserting data into database
print('Retrieving papers data:')
DOI, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount = papers_data(DOIs, keywords, yearsRange)
insert_publications(cursor, DOI, year, journal, authorshipKeywords, userKeywords,subjects, title, citationsCount)

print('Retrieving authors data:')
authorID, firstName, lastName, hIndex, subjectAreas, itemCitations, authorsCitations, documentsCount = authors_data(DOIs)
insert_authors(cursor, authorID, firstName, lastName, hIndex, subjectAreas, itemCitations, authorsCitations, documentsCount)

print('Retrieving organizations data:')
orgID, orgName, orgType, orgAddress, orgPostalCode, orgCity, orgState, orgCountry, parentID, parentName = orgs_data(DOIs)
insert_organizations(cursor, orgID, orgName, orgType, orgAddress, orgPostalCode, orgCity, orgState, orgCountry, parentID, parentName)

print('Matching papers with authors:')
papersDOIRelAuthors, authorsIDRelPapers = papers_and_authors(DOIs)
insert_publications_and_authors(cursor, papersDOIRelAuthors, authorsIDRelPapers)

print('Matching papers with organizations:')
papersDOIRelOrgs, orgsIDRelPapers = papers_and_orgs(DOIs)
insert_publications_and_organizations(cursor, papersDOIRelOrgs, orgsIDRelPapers)

print('Matching authors with organizations:')
authorsIDRelOrgs, orgsIDRelAuthors, currentOrgs = authors_and_organizations(DOIs)
insert_authors_and_publications(cursor, authorsIDRelOrgs, orgsIDRelAuthors, currentOrgs)

print('Claculating cultural distances per publication:')
citationsCount, minDIst, maxDist, avgDist = cultural_distances(DOIs)
instert_cultural_distances(cursor, DOIs, citationsCount, minDIst, maxDist, avgDist)

# committing changes and closing connection
commit_and_close(connection, cursor)