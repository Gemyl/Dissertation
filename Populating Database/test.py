from pybliometrics.scopus import CitationOverview, AbstractRetrieval
import pybliometrics.scopus.utils as psu

identifier = [85068268027]
co = CitationOverview(identifier, id_type='scopus_id', start=2019, end=2021).cc
print(co)