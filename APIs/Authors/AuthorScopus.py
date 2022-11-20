from pybliometrics.scopus import AuthorRetrieval

aut = AuthorRetrieval(35222178600, view='ENHANCED')
print(aut.affiliation_current)