from pybliometrics.scopus import AbstractRetrieval
from tqdm.auto import tqdm
from requests import get
import pandas as pd
import json


def FormatKeywords(keywords):

    keywords = keywords.split(', ')
    keywordsList = '('
    for i in range(len(keywords)):
        if i == len(keywords)-1:
            keywordsList = keywordsList + '{' + keywords[i] + '}'
        else:
            keywordsList = keywordsList + '{' + keywords[i] + '} ' + 'OR '

    keywordsList = keywordsList + ')'
    keywords = keywordsList

    return keywords


def ScopusSearch(url):

    req = get(url)
    if req.status_code == 200:
        content = json.loads(req.content)['search-results']
        TotalResults = content['opensearch:totalResults']
        StartIndex = content['opensearch:startIndex']
        Metadata = content['entry']

        return int(TotalResults), int(StartIndex), Metadata

    else:
        Error = json.loads(req.content)['service-error']['status']
        print(req.status_code, Error['statusText'])


def GetDOIs(keywords, yearsRange, subjects):

    DOIs = []
    Count = '&count=25'
    Term1 = '( {python} )'
    Term2 = keywords
    Terms = '( {} AND {} )'.format(Term1, Term2)
    Scope = 'TITLE-ABS-KEY'
    View = '&view=standard'
    Sort = '&sort=citedby_count'
    Date = '&date=' + str(yearsRange)
    ScopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'
    ScopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

    for Sub in tqdm(subjects):
        StartIndex = 0
        while True:
            Start = '&start={}'.format(StartIndex)
            Subj = '&subj={}'.format(Sub)

            Query = 'query=' + Scope + Terms + Date + Start + \
                     Count + Sort + Subj + ScopusAPIKey + View
            Url = ScopusBaseUrl + Query

            Total, StartIndex, Metadata = ScopusSearch(Url)

            for MetadataIndex in Metadata:
                try:
                    TempDOI = MetadataIndex['prism:doi']
                    DOIs.append(str(TempDOI))
                except:
                    continue

            Remain = Total - StartIndex - len(Metadata)

            if Remain > 0:
                StartIndex += 25
            else:
                break
    
    return DOIs


def GetMetadata(DOIs):

    row = {}
    removeDOIs = []
    maxAuthors = 0
    columnsNames = []

    for i in range(len(DOIs)):
        try:
            numAuthors = len(AbstractRetrieval(DOIs[i]).authors)
            if (numAuthors > maxAuthors) & (numAuthors < 10):
                maxAuthors = len(AbstractRetrieval(DOIs[i]).authors)
        except:
            removeDOIs.append(DOIs[i])

    for i in range(len(removeDOIs)):
        DOIs.remove(removeDOIs[i])
        
    columnsNames.append('DOI')
    for i in range(maxAuthors):
        columnsNames.append('Author ' + str(i+1) + ' ID')
        columnsNames.append('Author ' + str(i+1) + ' Name')

    table = pd.DataFrame(columns=columnsNames)

    for i in range(len(DOIs)):
        numAuthors = len(AbstractRetrieval(DOIs[i]).authors)
        row['DOI'] = str(DOIs[i])
        for j in range(maxAuthors):
            if j < numAuthors:
                row['Author ' +
                    str(j+1) + ' ID'] = [str(AbstractRetrieval(DOIs[i]).authors[j][0])]
                row['Author ' +
                    str(j+1) + ' Name'] = [AbstractRetrieval(DOIs[i]).authors[j][1]]
            else:
                row['Author ' + str(j+1) + ' ID'] = [' ']
                row['Author ' + str(j+1) + ' Name'] = [' ']

        rowDF = pd.DataFrame(row)
        table = pd.concat([table, rowDF], axis=0, ignore_index=True)
        row = {}

    return table
