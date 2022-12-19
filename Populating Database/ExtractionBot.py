from ScopusQuery import GetDOIs, GetMetadata, FormatKeywords
from MySQLserver import PushDataFrame

# Parameters given by user
keywords = input('Keywords: ')
keywordsFormat = FormatKeywords(keywords)
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')

# Finding DOIs of related publications
DOIs = GetDOIs(keywordsFormat, yearsRange, subjects)

# Creating DataFrame
table = GetMetadata(DOIs, keywords)

# Inserting DataFrame to MySQL database
PushDataFrame(table)