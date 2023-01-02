from pybliometrics.scopus import AuthorRetrieval

authorID = 57217424609
currentAffil = AuthorRetrieval(authorID, view='FULL').affiliation_current[0]
print(currentAffil)