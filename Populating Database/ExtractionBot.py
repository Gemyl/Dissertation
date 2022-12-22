from ScopusQueries import GetScopusDOIs, GetScopusPapers, GetScopusAuthors
import getpass

# Parameters given by user
keywords = input('Keywords: ')
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')
password = getpass.getpass('Password: ')

# Finding DOIs of related publications
DOIs = GetScopusDOIs(keywords, yearsRange, subjects)

# Retrieving data of papers and authors
GetScopusPapers(DOIs, password, keywords, yearsRange)
GetScopusAuthors(DOIs, password)