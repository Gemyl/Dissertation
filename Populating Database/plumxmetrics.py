from DataRetrieving import get_DOIs
from pybliometrics.scopus import PlumXMetrics, AbstractRetrieval

keywords = str(input('Keywords: '))
yearsRange = str(input('Years Range: '))
subjects = input('Subjects: ').split(', ')

DOIs = get_DOIs(keywords, yearsRange, subjects)


for doi in DOIs:
    metrics = PlumXMetrics(doi, id_type='doi').citation
    if metrics != None:
        print(f'DOI:{doi}| Metrics: {metrics}| Scopus Citations: {AbstractRetrieval(doi).citedby_count}')
        print(max([metric[1] for metric in metrics]))
    else:
        print(f'Metrics = None: {AbstractRetrieval(doi).citedby_count}')
