from pybliometrics.scopus import AffiliationRetrieval

af = AffiliationRetrieval(60000356)
print(af.org_type)