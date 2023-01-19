from gemysql import connect_to_MySQL, insert_publications, insert_authors, insert_organizations, \
     insert_publications_and_authors, insert_publications_and_organizations, commit_and_close, insert_authors_and_organizations, \
     instert_cultural_distances
from scientodata import get_DOIs, papers_data, authors_data, orgs_data, papers_and_authors, papers_and_orgs, \
     authors_and_organizations
from distances import geographical_distances, organizational_distances
from getpass import getpass

# parameters given by user
keywords = str(input('Keywords: '))
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')
password = getpass('Password: ')

# finding DOIs of related publications
print('Retrieving DOIs:')
DOIs = get_DOIs(keywords, yearsRange, subjects)
# establishing connection with database
connection, cursor, error = connect_to_MySQL(password)

# retrieving and inserting data into database
print('\nRetrieving papers data:')
DOI, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount = papers_data(DOIs, keywords, yearsRange)
print('Inserting papers data to database:')
insert_publications(cursor, DOI, year, journal, authorshipKeywords, userKeywords,subjects, title, citationsCount)

print('\nRetrieving authors data:')
authorID, firstName, lastName, hIndex, subjectAreas, itemCitations, authorsCitations, documentsCount = authors_data(DOIs)
print('Inserting authors data to database:')
insert_authors(cursor, authorID, firstName, lastName, hIndex, subjectAreas, itemCitations, authorsCitations, documentsCount)

print('\nRetrieving organizations data:')
orgID, orgName, orgType1, orgType2, orgAddress, orgPostalCode, orgCity, orgState, orgCountry, orgType1Grp, orgType2Grp, cityGrp \
= orgs_data(DOIs)
print('Inserting organizations data to database:')
insert_organizations(cursor, orgID, orgName, orgType1, orgType2, orgAddress, orgPostalCode, orgCity, orgState, orgCountry)

print('\nMatching papers with authors:')
pubDOI, authorID = papers_and_authors(DOIs)
print('Inserting papers-authors matching data to database:')
insert_publications_and_authors(cursor, pubDOI, authorID)

print('\nMatching papers with organizations:')
pubDOI, orgIDTemp = papers_and_orgs(DOIs, orgID)
print('Inserting papers-organizations matching data to database:')
insert_publications_and_organizations(cursor, pubDOI, orgIDTemp)

print('\nMatching authors with organizations:')
authorID, orgIDTemp = authors_and_organizations(DOIs, orgID)
print('Inserting authors-organizations mathcing data to database:')
insert_authors_and_organizations(cursor, authorID, orgIDTemp)

print('\nCalculating distances per publication:')
minDIst, maxDist, avgDist = geographical_distances(cityGrp)
minOrgDist, maxOrgDist, avgOrgDist = organizational_distances(orgType1Grp)
print('\Inserting calculated distances to database:')
instert_cultural_distances(cursor, DOIs, citationsCount, minDIst, maxDist, avgDist, minOrgDist, maxOrgDist, avgOrgDist)

# committing changes and closing connection
commit_and_close(connection, cursor)