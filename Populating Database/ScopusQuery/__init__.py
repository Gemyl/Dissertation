from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
from TextFormating import FormatKeywords, ListToString
from DataFramesForming import FindMaxNumAuthors
from MySQLserver import InsertDataFrame
from tqdm.auto import tqdm
from requests import get
import pandas as pd
import json


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
    Term2 = FormatKeywords(keywords)
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


def GetPapers(DOIs, keywords):
    row = {}
    columnsNames = []
    columnsNames.append('DOI')
    columnsNames.append('Year')
    columnsNames.append('Journal')
    columnsNames.append('Authorship Keywords')
    columnsNames.append('User Keywords')
    columnsNames.append('Subjects')
    columnsNames.append('Title')
    columnsNames.append('Citations Count')

    maxAuthors, DOIs = FindMaxNumAuthors(DOIs)
    for i in range(maxAuthors):
        columnsNames.append('Author ' + str(i+1) + ' ID')
        columnsNames.append('Author ' + str(i+1) + ' Name')

    columnsNames = pd.DataFrame(columns=columnsNames)

    for i in range(len(DOIs)):
        row['DOI'] = str(DOIs[i])
        row['Year'] = str(AbstractRetrieval(DOIs[i], view='FULL').date_created[0])
        row['Journal'] = str(AbstractRetrieval(DOIs[i]).publisher)
        row['User Keywords'] = keywords
        row['Subjects'] = str(AbstractRetrieval(DOIs[i], view='FULL').subject_areas)
        row['Title'] = AbstractRetrieval(DOIs[i], view='FULL').title
        row['Citations Count'] = str(AbstractRetrieval(DOIs[i]).citedby_count)
        row['Authorship Keywords'] = ListToString(AbstractRetrieval(DOIs[i], view='FULL').authkeywords)
        
        numAuthors = len(AbstractRetrieval(DOIs[i]).authors)
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
        table = pd.concat([columnsNames, rowDF], axis=0, ignore_index=True)
        try:
            InsertDataFrame(table, 'papers')
        except:
            continue
        row = {}


def GetAuthors(DOIs):
    row = {}
    columnsNames = []
    columnsNames.append('Scopus_ID')
    columnsNames.append('Indexed_Name')
    columnsNames = pd.DataFrame(columns=columnsNames)

    for i in range(len(DOIs)):
        authors = AbstractRetrieval(DOIs[i]).authors
        for author in authors:
            row['Scopus_ID'] = [str(AuthorRetrieval(author[0]).identifier)]
            row['Indexed_Name'] = [author[1]]
            rowDF = pd.DataFrame(row)
            tableTemp = pd.concat([columnsNames, rowDF], axis=0, ignore_index=True)
            try:
                InsertDataFrame(tableTemp, 'authors')
            except:
                continue
            row = {}