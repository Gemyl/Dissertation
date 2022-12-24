from ScopusQueries import get_DOIs_Scopus, get_papers_data_Scopus, get_authors_data_Scopus, get_author_degrees_Scopus
import pandas as pd

# Parameters given by user
keywords = input('Keywords: ')
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')

# Finding DOIs of related publications
DOIs = get_DOIs_Scopus(keywords, yearsRange, subjects)

# Retrieving data of papers
DOIs, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount \
 = get_papers_data_Scopus(DOIs, keywords, yearsRange)

# Retrieving data of authors
authorID, indexedName = get_authors_data_Scopus(DOIs)

# # Printing results
# papersDF = pd.DataFrame({'DOI':DOIs, 'Year':year, 'Journal':journal, 'Authorship\'s Keywords':authorshipKeywords, \
#                     'User\'s Keywords':userKeywords, 'Subject':subjects, 'Title':title, 'Citations Count': citationsCount})

# authorsDF = pd.DataFrame({'ID':authorID, 'Indexed Name':indexedName})

# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#     print(papersDF)
#     print(authorsDF)
