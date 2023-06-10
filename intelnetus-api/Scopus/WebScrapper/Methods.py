from Preprocessing.Methods import buildKeywordsQuery
from requests import get
from tqdm import tqdm
import json

def getMetadata(keywords, yearPublished, fields, booleans, apiKey):

    # DOIs list
    dois = []

    # query parameters
    count = '&count=25'
    terms = f'( {buildKeywordsQuery(keywords, booleans)} )'
    scope = 'TITLE-ABS-KEY'
    view = '&view=standard'
    sort = '&sort=citedby_count'
    date = '&date=' + str(yearPublished)
    scopusAPIKey = f'&apiKey={apiKey}'
    scopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

    # retrieving publications DOIs
    print("Retrieving DOIs ...")
    for field in tqdm(fields):
        
        errorCounter = 0
        startIndex = 0
        while True:
            start = f"&start={startIndex}"
            currentField = f"&subj={field}"
            
            # building GET query
            query = 'query=' + scope + terms + date + start + \
                count + sort + currentField + scopusAPIKey + view
            url = scopusBaseUrl + query

            req = get(url)
            # if request is successful, get DOIs
            if req.status_code == 200:
                content = json.loads(req.content)['search-results']
                totalResults = int(content['opensearch:totalResults'])
                startIndex = int(content['opensearch:startIndex'])
                metadata = content['entry']
            # else print the error cause
            else:
                Error = json.loads(req.content)['service-error']['status']
                print(req.status_code, Error['statusText'])
                errorCounter += 1

            for md in metadata:
                try:
                    TempDOI = md['prism:doi']
                    dois.append(str(TempDOI))
                except:
                    pass

            remainingData = totalResults - startIndex - len(metadata)

            # if there are any records remained, update startIndex and start the next loop
            if ((remainingData > 0) & (errorCounter < 10)):
                startIndex += 25
            # else exit the loop and continue with the next subject
            else:
                break

    return dois            