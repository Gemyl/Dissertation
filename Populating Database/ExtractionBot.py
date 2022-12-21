from ScopusQueries import GetScopusDOIs, GetScopusPapers, GetScopusAuthors
# Parameters given by user
keywords = input('Keywords: ')
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')

# Finding DOIs of related publications
DOIs = GetScopusDOIs(keywords, yearsRange, subjects)

# Retrieving data of papers and authors
GetScopusPapers(DOIs, keywords, yearsRange)
GetScopusAuthors(DOIs)
