from pybliometrics.scopus import AbstractRetrieval
from tqdm.auto import tqdm
from requests import get
import json


DOIs = []
Scores = []
Publisher = []
Language = []
PageRange =[]
CreationDate = []
AuthorsCount = []
CitationsCount = []
PublicationName = []
ReferencesCount = []
AffiliationsCount = []


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


ScopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

Scope = 'TITLE-ABS-KEY'

Term1 = '( {python} )'
Term2 = '({artificial intelligence})'
Terms = '( {} AND {} )'.format(Term1, Term2)

ScopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'

Date = '&date=2022'

Count = '&count=25'

Sort = '&sort=citedby_count'

View = '&view=standard'

Subjects = subjects = ['ENER']


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


print(len(DOIs))

for i in tqdm(range(len(DOIs))):

    ScopusData = AbstractRetrieval(DOIs[i], view= 'FULL')

    try:
        AffiliationsCount.append(str(len(ScopusData.affiliation)))
    except:
        AffiliationsCount.append('-')

    try:
        AuthorsCount.append(str(len(ScopusData.authors)))
    except:
        AuthorsCount.append('-')

    try:
        CitationsCount.append(str(ScopusData.citedby_count))
    except:
        CitationsCount.append('-')

    try:
        CreationDate.append(str(ScopusData.date_created))
    except:
        CreationDate.append('-')

    try:    
        Language.append(str(ScopusData.language))
    except:
        Language.append('-')
    
    try:
        PageRange.append(str(ScopusData.pageRange))
    except:
        PageRange.append('-')

    try:
        PublicationName.append(str(ScopusData.publicationName))
    except:
        PublicationName.append('-')

    try:
        Publisher.append(str(ScopusData.publisher))
    except:
        Publisher.append('-')

    try:
        ReferencesCount.append(str(ScopusData.refcount))
    except:
        ReferencesCount.append('-')


    # BaseURL = "https://api.altmetric.com/v1/doi/10.1016/j.softx.2019.100263"
    # AltmetURL = BaseURL + DOIs[i]
    # req = get(AltmetURL)
    # if req.status_code == 200:
    #     AltmerticData = json.loads(req.text.encode('ascii', errors='ignore'))
    #     Scores.append(AltmerticData['score'])
    # else:
    #     Scores.append('Not found')

for i in range(len(DOIs)):
    print( AffiliationsCount[i] + ', ' + AuthorsCount[i] + ', ' + CitationsCount[i] + ', ' + ReferencesCount[i] + ', ' +
           CreationDate[i] + ', ' + Language[i] + ', ' + PageRange[i] + ', ' + PublicationName[i] + ', ' + Publisher[i]  + '.') 

