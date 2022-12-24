from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
from TextFormating import format_keywords, list_to_string
from tqdm.auto import tqdm
from requests import get
import json


def get_DOIs(keywords, yearsRange, subjects):

    DOIs = []
    count = '&count=25'
    term1 = '( {python} )'
    term2 = format_keywords(keywords)
    terms = '( {} AND {} )'.format(term1, term2)
    scope = 'TITLE-ABS-KEY'
    view = '&view=standard'
    sort = '&sort=citedby_count'
    date = '&date=' + str(yearsRange)
    scopusAPIKey = '&apiKey=33a5ac626141313c10881a0db097b497'
    scopusBaseUrl = 'http://api.elsevier.com/content/search/scopus?'

    for sub in tqdm(subjects):

        startIndex = 0

        while True:

            start = '&start={}'.format(startIndex)
            subj = '&subj={}'.format(sub)

            query = 'query=' + scope + terms + date + start + \
                     count + sort + subj + scopusAPIKey + view
            url = scopusBaseUrl + query

            req = get(url)
            if req.status_code == 200:
                content = json.loads(req.content)['search-results']
                totalResults = int(content['opensearch:totalResults'])
                startIndex = int(content['opensearch:startIndex'])
                metadata = content['entry']
            else:
                Error = json.loads(req.content)['service-error']['status']
                print(req.status_code, Error['statusText'])

            for metadataIndex in metadata:
                try:
                    TempDOI = metadataIndex['prism:doi']
                    DOIs.append(str(TempDOI))
                except:
                    continue

            Remain = totalResults - startIndex - len(metadata)

            if Remain > 0:
                startIndex += 25
            else:
                break
    
    return DOIs


def papers_data(DOIs, keywords, yearsRange):

    DOI = []
    year = []
    title = []
    journal = []
    subjects = []
    userKeywords = []
    citationsCount = []
    authorshipKeywords = []
    
    for i in range(len(DOIs)):

        try:
            year.append(yearsRange)
        except:
            year.append(' ')
        
        try:    
            DOI.append(str(DOIs[i]))
        except:
            DOI.append(' ')
        try:    
            userKeywords.append(keywords)
        except:
            userKeywords.append(' ')

        try:
            journal.append(str(AbstractRetrieval(DOIs[i]).publisher))
        except:
            journal.append(' ')

        try:
            title.append(AbstractRetrieval(DOIs[i], view='FULL').title)
        except:
            title.append(' ')

        try:
            citationsCount.append(str(AbstractRetrieval(DOIs[i]).citedby_count))
        except:
            citationsCount.append(' ')

        try:
            subjects.append(', '.join(str(sub[0]) for sub in AbstractRetrieval(DOIs[i], view='FULL').subject_areas))
        except:
            subjects.append(' ')

        try:    
            authorshipKeywords.append(list_to_string(AbstractRetrieval(DOIs[i], view='FULL').authkeywords))
        except:
            authorshipKeywords.append(' ')

    return DOI, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount 


def authors_data(DOIs):

    eid = []
    orcid = []
    hIndex = []
    identifier = []  
    indexedName = []
    itemCitations = []
    coauthorsCount = []
    documentsCount = []
    subjectedAreas = []
    authorsCitations = []  

    for i in range(len(DOIs)):

        authors = AbstractRetrieval(DOIs[i]).authors

        for author in authors:

            authorInfo = AuthorRetrieval(author[0])

            if identifier.count(authorInfo.identifier) == 0:                   

                try:
                    identifier.append(authorInfo.identifier)
                except:
                    identifier.append(' ')

                try:
                    eid.append(authorInfo.eid)
                except:
                    eid.append(' ')

                try:
                    orcid.append(authorInfo.orcid)
                except:
                    orcid.append(' ')

                try:
                    indexedName.append(authorInfo.indexed_name)
                except:
                    indexedName.append(' ')

                try:
                    subjectedAreas.append(list(sub[0] for sub in authorInfo.subject_areas))
                except:
                    subjectedAreas.append('')  

                try:
                    hIndex.append(authorInfo.h_index)
                except:
                    hIndex.append(' ')

                try:
                    itemCitations.append(authorInfo.citation_count)
                except:
                    itemCitations.append(' ')

                try:
                    authorsCitations.append(authorInfo.cited_by_count)
                except:
                    authorsCitations.append(' ')

                try:
                    documentsCount.append(authorInfo.document_count)
                except:
                    documentsCount.append(' ')

                try:
                    coauthorsCount.append(authorInfo.coauthor_count)
                except:
                    coauthorsCount.append(' ')

    return identifier, eid, orcid, indexedName, hIndex, subjectedAreas, \
        itemCitations, authorsCitations, documentsCount, coauthorsCount 


def orgs_data(DOIs):

    eid = []
    name = []
    city = []
    type = []
    state = []
    country = []
    address = []
    postalCode = []
    identifier = []

    for i in range(len(DOIs)):

        for org in AbstractRetrieval(DOIs[i]).affiliation:

            orgInfo = AffiliationRetrieval(org[0])

            if (identifier.count(orgInfo.affiliation_name) == 0) & name.count(orgInfo.affiliation_name) == 0 \
                & (any(orgName in name for orgName in orgInfo.name_variants)):

                    try:
                        identifier.append(orgInfo.identifier)
                    except:
                        identifier.append(' ')

                    try:
                        eid.append(orgInfo.eid)
                    except:
                        eid.append(' ')

                    try:
                        name.append(orgInfo.affiliation_name)
                    except:
                        name.append(' ')

                    try:
                        type.append(orgInfo.org_type)
                    except:
                        type.append(' ')

                    try:
                        address.append(orgInfo.address)
                    except:
                        address.append(' ')
                    
                    try:
                        postalCode.append(orgInfo.postal_code)
                    except:
                        postalCode.append(' ')

                    try:
                        city.append(orgInfo.city)
                    except:
                        city.append(' ')

                    try:
                        state.append(orgInfo.state)
                    except:
                        state.append(' ')

                    try:
                        country.append(orgInfo.country)
                    except:
                        country.append(' ')

    return identifier, eid, name, type, address, postalCode, city, state, country