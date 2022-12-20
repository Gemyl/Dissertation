from ScopusQuery import GetDOIs, GetPapers, GetAuthors

# Parameters given by user
keywords = input('Keywords: ')
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')

# Finding DOIs of related publications
DOIs = GetDOIs(keywords, yearsRange, subjects)

# Retrieving data of papers and authors
GetPapers(DOIs, keywords)
GetAuthors(DOIs)