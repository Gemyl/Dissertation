from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
from tqdm.auto import tqdm
import pandas as pd
import requests
import json

DOIs = []
Authors = []
AuthorsNames = []
citations = []

#-------------- Function for Scopus Database Search -----------------#
def search_scopus(url):
    res = requests.get(url)
    if res.status_code == 200:
        content = json.loads(res.content)['search-results']
        total = content['opensearch:totalResults']
        start = content['opensearch:startIndex']
        metaData = content['entry']

        return int(total), int(start), metaData
    
    else:
        error = json.loads(res.content)['service-error']['status']
        print(res.status_code, error['statusText'])
#--------------------------------------------------------------------#


#------------------- Fomration of Query URL -----------------------#
base_url = 'http://api.elsevier.com/content/search/scopus?'

scope = 'TITLE-ABS-KEY'

term1 = '( {python} )'
term2 = '({artificial intelligence})'
terms = '( {} AND {} )'.format(term1, term2)

apiKey = '&apiKey=33a5ac626141313c10881a0db097b497'
date = '&date=2018'

count = '&count=25'
sort = '&sort=citedby-count'
view = '&view=standard'

subjects = ['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
            'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
            'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
            'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']
#-----------------------------------------------------------------#

#-------------------- Retrieving Metadata ------------------------#
for sub in tqdm(subjects):

    start_index = 0
    
    while True:

        start = '&start={}'.format(start_index)
        subj = '&subj={}'.format(sub)
        query = 'query=' + scope + terms + date + start + count + sort + subj + apiKey + view

        url = base_url + query

        total, start_index, MetaData  = search_scopus(url)

        for i in range(len(MetaData)):
            try:
                DOIs.append(str(MetaData[i]['prism:doi']))
            except:
                continue
           
 
        remain = total - start_index - len(MetaData)

        if remain > 0:
            start_index += 25
        else:
            break
#--------------------------------------------------------#

for doi in tqdm(DOIs):
        ab = AbstractRetrieval(doi)
        for author in ab.authors:
            Authors.append(author)

AuthorsDF = pd.DataFrame(Authors)

for i in range(6):
    auid = AuthorsDF.loc[i].at['auid']
    ab = AuthorRetrieval(auid)
    AuthorsNames.append(ab.given_name)

for author in AuthorsNames:
    print(author.encode(errors='ignore'))