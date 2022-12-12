from tqdm.auto import tqdm
from requests import get
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


def GetDOIs(Keywords, YearsRange, Subjects):

    ScopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

    Scope = 'TITLE-ABS-KEY'

    Term1 = '( {python} )'
    Term2 = '({' + str(Keywords) + '})'
    Terms = '( {} AND {} )'.format(Term1, Term2)

    ScopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'

    Date = '&date=' + str(YearsRange)

    Count = '&count=25'

    Sort = '&sort=citedby_count'

    View = '&view=standard'

    DOIs = []

    for Sub in tqdm(Subjects):

        StartIndex = 0

        while True:

            Start = '&start={}'.format(StartIndex)
            Subj = '&subj={}'.format(Sub)
            Query = 'query=' + Scope + Terms + Date + Start + Count + Sort + Subj + ScopusAPIKey + View

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