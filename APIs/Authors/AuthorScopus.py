from pybliometrics.scopus import AuthorRetrieval, AbstractRetrieval

paperInfo = AbstractRetrieval('10.1016/S0261-5177(02)00047-X').authors
paperAffil = AbstractRetrieval('10.1016/S0261-5177(02)00047-X').affiliation

authorAffil = AuthorRetrieval(6506504371).affiliation_history
print(authorAffil)
print(paperAffil)