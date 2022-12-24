from DataRetrieving import get_DOIs, papers_data, authors_data, orgs_data
import pandas as pd

# parameters given by user
keywords = input('Keywords: ')
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')

# finding DOIs of related publications
DOIs = get_DOIs(keywords, yearsRange, subjects)

# retrieving data of papers
DOIs, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount \
     = papers_data(DOIs, keywords, yearsRange)

# retrieving data of authors
authorID, eid, orcid, name, hIndex, subjectAreas, itemCitations, authorsCitations, \
    documentsCount, coauthorsCount = authors_data(DOIs)

# retrieving data of organizations
orgID, orgEID, orgName, orgType, orgAddress, orgPostalCode, orgCity, orgState, \
     orgCountry =  orgs_data(DOIs)

# printing results
papers = pd.DataFrame({'DOI':DOIs, 'Year':year, 'Journal':journal, 'Authorship\'s Keywords':authorshipKeywords, \
    'User\'s Keywords':userKeywords, 'Subject':subjects, 'Title':title, 'Citations Count': citationsCount})

authors = pd.DataFrame({'ID':authorID, 'EID':eid, 'ORCID':orcid, 'Indexed Name':name, 'h-Index':hIndex, \
    'Subjected Areas':subjectAreas, 'Item Citrations': itemCitations, 'Authors Citations':authorsCitations, \
    'Documents Count':documentsCount, 'Co-authors Count':coauthorsCount})

organizations = pd.DataFrame({'ID':orgID, 'EID':orgEID, 'Name':orgName, 'Type':orgType, 'Address':orgAddress, \
    'Postal Code':orgPostalCode, 'City':orgCity, 'State':orgState, 'Country':orgCountry})

with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):

    print(papers)
    print(authors)
    print(organizations)