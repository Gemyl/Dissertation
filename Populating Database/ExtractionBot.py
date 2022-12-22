from ScopusQueries import get_DOIs, get_papers_data, get_authors_data
import getpass

# Parameters given by user
keywords = input('Keywords: ')
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')
password = getpass.getpass('Password: ')

# Finding DOIs of related publications
DOIs = get_DOIs(keywords, yearsRange, subjects)

# Retrieving data of papers and authors
get_papers_data(DOIs, password, keywords, yearsRange)
get_authors_data(DOIs, password)