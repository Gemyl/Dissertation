from MySQLpackage import insert_to_MySQL, add_authors, find_authors_number, remove_nulls
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
from TextFormating import format_keywords, list_to_string
from DataFramesForming import find_max_authors
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


def get_DOIs(keywords, yearsRange, subjects):

    DOIs = []
    Count = '&count=25'
    Term1 = '( {python} )'
    Term2 = format_keywords(keywords)
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


def get_papers_data(DOIs, password, keywords, yearsRange):

    row = {}
    columnsNames = []
    columnsNames.append('DOI')
    columnsNames.append('Year')
    columnsNames.append('Journal')
    columnsNames.append('Authorship_Keywords')
    columnsNames.append('User_Keywords')
    columnsNames.append('Subjects')
    columnsNames.append('Title')
    columnsNames.append('Citations_Count')

    maxAuthorsSearch, DOIs = find_max_authors(DOIs)
    try:
        maxAuthorsTable = find_authors_number('papers', password)
        if (maxAuthorsSearch > maxAuthorsTable):
            add_authors('papers', password, maxAuthorsSearch, int(maxAuthorsTable))
    except:
        pass

    for i in range(maxAuthorsSearch):
        columnsNames.append('Author_' + str(i+1) + '_ID')
        columnsNames.append('Author_' + str(i+1) + '_Name')

    columnsNames = pd.DataFrame(columns=columnsNames)

    for i in range(len(DOIs)):
        row['DOI'] = str(DOIs[i])
        row['Year'] = yearsRange
        row['Journal'] = str(AbstractRetrieval(DOIs[i]).publisher)
        row['Authorship_Keywords'] = list_to_string(AbstractRetrieval(DOIs[i], view='FULL').authkeywords)
        row['User_Keywords'] = keywords
        row['Subjects'] = str(AbstractRetrieval(DOIs[i], view='FULL').subject_areas)
        row['Title'] = AbstractRetrieval(DOIs[i], view='FULL').title
        row['Citations_Count'] = str(AbstractRetrieval(DOIs[i]).citedby_count)
        
        numAuthors = len(AbstractRetrieval(DOIs[i]).authors)
        for j in range(maxAuthorsSearch):
            if j < numAuthors:
                row['Author_' +
                    str(j+1) + '_ID'] = [str(AbstractRetrieval(DOIs[i]).authors[j][0])]
                row['Author_' +
                    str(j+1) + '_Name'] = [AbstractRetrieval(DOIs[i]).authors[j][1]]
            else:
                row['Author_' + str(j+1) + '_ID'] = [' ']
                row['Author_' + str(j+1) + '_Name'] = [' ']

        rowDF = pd.DataFrame(row)
        table = pd.concat([columnsNames, rowDF], axis=0, ignore_index=True)

        try:
            insert_to_MySQL(table, 'papers', password)
        except:
            pass

        row = {}
        


def get_authors_data(DOIs, password):

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
                insert_to_MySQL(tableTemp, 'authors', password)
            except:
                continue
            row = {}