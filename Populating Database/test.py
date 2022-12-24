from pybliometrics.scopus import AuthorRetrieval

print(list(t[0] for t in AuthorRetrieval('9-s2.0-57217424609').subject_areas))