from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval, PlumXMetrics
from textformating import format_keywords, list_to_string
from tqdm.auto import tqdm
from requests import get
import json

# function that retrieves the DOIs of papers from Scopus
# based on input keywords, range of years and  subjects


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

        # startIndex is used to summarize all the previous DOIs
        # that have been retrieved for a given subject
        startIndex = 0

        while True:

            start = '&start={}'.format(startIndex)
            subj = '&subj={}'.format(sub)

            query = 'query=' + scope + terms + date + start + \
                count + sort + subj + scopusAPIKey + view
            url = scopusBaseUrl + query

            # sending request to Scopus
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

            # 'totalResults' is the number of all items that search has been resulted in
            # 'startIndex' is the number of items whose data have been already obtained
            # the length of 'metadata' is the number of items whose data are going to be extracted
            Remain = totalResults - startIndex - len(metadata)

            if Remain > 0:
                startIndex += 25
            else:
                break

    return DOIs


# this function retrieves papers data from Scopus
def papers_data(DOIs, keywords, yearsRange):

    DOI = []
    year = []
    title = []
    subjects = []
    publisher = []
    userKeywords = []
    citationsCount = []
    authorsKeywords = []

    # in this loop every DOI is accessed
    # each DOI corresponds to a paper
    for doi in tqdm(DOIs):

        paperInfo = AbstractRetrieval(doi, view='FULL')

        DOI.append(str(doi))
        year.append(yearsRange)
        userKeywords.append(keywords)
        title.append(str(paperInfo.title).replace('\'', '\\' + '\''))
        publisher.append(str(paperInfo.publisher))
        authorsKeywords.append(list_to_string(paperInfo.authkeywords))
        subjects.append(', '.join(str(sub[0]).lower()
                                  for sub in paperInfo.subject_areas))

        # paper'smaximum number of citations
        maxCitations = paperInfo.citedby_count
        plumxCitations = PlumXMetrics(doi, id_type='doi').citation
        if plumxCitations != None:
            plumxCitations = max([citation[1]
                                  for citation in plumxCitations])
            maxCitations = max(maxCitations, plumxCitations)
        citationsCount.append(str(maxCitations))

    return DOI, year, publisher, authorsKeywords, userKeywords, subjects, title, citationsCount


# this function retrieves authors data from Scopus
def authors_data(DOIs):

    # each list corresponds to an author's attribute
    hIndex = []
    lastName = []
    firstName = []
    identifier = []
    indexedName = []
    itemCitations = []
    documentsCount = []
    subjectedAreas = []
    authorsCitations = []

    # in this loop every DOI is accessed
    for doi in tqdm(DOIs):

        # getting a paper's authors
        authors = AbstractRetrieval(doi).authors

        # in this loop every author is accessed
        for author in authors:
            # getting all the available information for each author
            authorInfo = AuthorRetrieval(author[0])

            # checking if an author has been already accesed during this search
            if identifier.count(authorInfo.identifier) == 0:
                identifier.append(str(authorInfo.identifier))
                firstName.append(str(authorInfo.given_name))
                lastName.append(str(authorInfo.surname))
                indexedName.append(str(authorInfo.indexed_name))
                subjectedAreas.append(
                    ', '.join(str(sub[0]).lower() for sub in authorInfo.subject_areas))
                hIndex.append(str(authorInfo.h_index))
                itemCitations.append(str(authorInfo.citation_count))
                authorsCitations.append(str(authorInfo.cited_by_count))
                documentsCount.append(str(authorInfo.document_count))

    return identifier, firstName, lastName, subjectedAreas, hIndex, \
        itemCitations, authorsCitations, documentsCount


# this function retrieves orgnizations data from Scopus
def orgs_data(DOIs):

    # fields for organizations table
    name = []
    city = []
    type1 = []
    type2 = []
    state = []
    country = []
    address = []
    tempOrgs = []
    postalCode = []
    identifier = []

    # fields needed for organizational distances calculation
    type1Temp = []
    type2Temp = []
    type1Dist = []
    type2Dist = []
    cityTemp = []
    cityDist = []

    # in this loop every DOI is accessed
    for doi in tqdm(DOIs):

        paperOrgs = AbstractRetrieval(doi).affiliation
        for org in paperOrgs:

            if str(org[0]) not in identifier:
                orgInfo = AffiliationRetrieval(org[0])
                name.append(str(org[1]))
                city.append(str(orgInfo.city))
                state.append(str(orgInfo.state))
                country.append(str(orgInfo.country))
                address.append(str(orgInfo.address))
                postalCode.append(str(orgInfo.postal_code))
                identifier.append(str(orgInfo.identifier))

                if (orgInfo.org_type == 'univ'):
                    type1.append('Academic')
                    type2.append('University - College')
                elif orgInfo.org_type == 'coll':
                    type1.append('Academic')
                    type2.append('University - College')
                elif orgInfo.org_type == 'sch':
                    type1.append('Academic')
                    type2.append('School')
                elif orgInfo.org_type == 'res':
                    type1.append('Academic')
                    type2.append('Research Institute')
                elif orgInfo.org_type == 'gov':
                    type1.append('Government')
                    type2.append(' ')
                elif orgInfo.org_type == 'assn':
                    type1.append('Association')
                    type2.append(' ')
                elif orgInfo.org_type == 'corp':
                    type1.append('Business')
                    type2.append(' ')
                elif orgInfo.org_type == 'non':
                    type1.append('Non-profit')
                    type2.append(' ')
                elif ('university' in name[len(name)-1].lower()) | ('universiti' in name[len(name)-1].lower()) | \
                    ('universidade' in name[len(name)-1].lower()) | ('universidad' in name[len(name)-1].lower()) | \
                    ('college' in name[len(name)-1].lower()) | ('universität' in name[len(name)-1].lower()) | \
                    ('department' in name[len(name)-1].lower()) | ('dept.' in name[len(name)-1].lower()) | \
                        ('uniwersytet' in name[len(name)-1].lower()) | ('dipartimento' in name[len(name)-1].lower()):
                    type1.append('Academic')
                    type2.append('University - College')
                elif ('academy' in name[len(name)-1].lower()) | ('academic' in name[len(name)-1].lower()):
                    type1.append('Academic')
                    type2.append('Academy')
                elif ('school' in name[len(name)-1].lower()) | ('faculty' in name[len(name)-1].lower()):
                    type1.append('Academic')
                    type2.append('School')
                elif ('research' in name[len(name)-1].lower()) | ('researchers' in name[len(name)-1].lower()):
                    type1.append('Academic')
                    type2.append('Research Institute')
                elif ('inc.' in name[len(name)-1].lower()) | ('inc' in name[len(name)-1].lower()) | \
                        ('ltd.' in name[len(name)-1].lower()) | ('ltd' in name[len(name)-1].lower()):
                    type1.append('Business')
                    type2.append(' ')
                elif ('association' in name[len(name)-1].lower()):
                    type1.append('Association')
                    type2.append(' ')
                elif ('non-profit' in name[len(name)-1].lower()):
                    type1.append('Non-profit')
                    type2.append(' ')
                elif ('government' in name[len(name)-1].lower()) | ('public' in name[len(name)-1].lower()) | \
                    ('state' in name[len(name)-1].lower()) | ('national' in name[len(name)-1].lower()) | \
                    ('federal' in name[len(name)-1].lower()) | ('royal' in name[len(name)-1].lower()) | \
                        ('federate' in name[len(name)-1].lower()) | ('confederate' in name[len(name)-1].lower()):
                    type1.append('Government')
                    type2.append(' ')
                elif ('international' in name[len(name)-1].lower()) | ('intergovernmental' in name[len(name)-1].lower()):
                    type1.append('International')
                    type2.append(' ')
                else:
                    print(name[len(name)-1].lower())
                    type1.append('Other')
                    type2.append(' ')

                tempOrgs.append(org[0])
                type1Temp.append(str(type1[len(type1)-1]))
                type2Temp.append(str(type2[len(type2)-1]))
                cityTemp.append(str(city[len(city)-1]))

            authors = AbstractRetrieval(doi).authors
            for author in authors:
                authorID = author[0]
                for org in AuthorRetrieval(authorID).affiliation_history:

                    if (org[1] in tempOrgs) & (str(org[0]) not in identifier):
                        orgInfo = AffiliationRetrieval(org[0])
                        name.append(str(org[5] + ' - ' + org[6]))
                        city.append(str(orgInfo.city))
                        state.append(str(orgInfo.state))
                        country.append(str(orgInfo.country))
                        address.append(str(orgInfo.address))
                        postalCode.append(str(orgInfo.postal_code))
                        identifier.append(str(orgInfo.identifier))

                        if (orgInfo.org_type == 'univ'):
                            type1.append('Academic')
                            type2.append('University - College')
                        elif orgInfo.org_type == 'coll':
                            type1.append('Academic')
                            type2.append('University - College')
                        elif orgInfo.org_type == 'res':
                            type1.append('Academic')
                            type2.append('Research Institute')
                        elif orgInfo.org_type == 'gov':
                            type1.append('Government')
                            type2.append(' ')
                        elif orgInfo.org_type == 'assn':
                            type1.append('Association')
                            type2.append(' ')
                        elif orgInfo.org_type == 'corp':
                            type1.append('Business')
                            type2.append(' ')
                        elif orgInfo.org_type == 'non':
                            type1.append('Non-profit')
                            type2.append(' ')
                        elif ('university' in name[len(name)-1].lower()) | ('universiti' in name[len(name)-1].lower()) | \
                            ('universidade' in name[len(name)-1].lower()) | ('universidad' in name[len(name)-1].lower()) | \
                            ('college' in name[len(name)-1].lower()) | ('universität' in name[len(name)-1].lower()) | \
                            ('department' in name[len(name)-1].lower()) | ('dept.' in name[len(name)-1].lower()) | \
                                ('uniwersytet' in name[len(name)-1].lower()) | ('dipartimento' in name[len(name)-1].lower()):
                            type1.append('Academic')
                            type2.append('University - College')
                        elif ('academy' in name[len(name)-1].lower()) | ('academic' in name[len(name)-1].lower()):
                            type1.append('Academic')
                            type2.append('Academy')
                        elif ('school' in name[len(name)-1].lower()) | ('faculty' in name[len(name)-1].lower()):
                            type1.append('Academic')
                            type2.append('School')
                        elif ('research' in name[len(name)-1].lower()) | ('researchers' in name[len(name)-1].lower()):
                            type1.append('Academic')
                            type2.append('Research Institute')
                        elif ('inc.' in name[len(name)-1].lower()) | ('inc' in name[len(name)-1].lower()) | \
                                ('ltd.' in name[len(name)-1].lower()) | ('ltd' in name[len(name)-1].lower()):
                            type1.append('Business')
                            type2.append(' ')
                        elif ('association' in name[len(name)-1].lower()):
                            type1.append('Association')
                            type2.append(' ')
                        elif ('non-profit' in name[len(name)-1].lower()):
                            type1.append('Non-profit')
                            type2.append(' ')
                        elif ('government' in name[len(name)-1].lower()) | ('public' in name[len(name)-1].lower()) | \
                            ('state' in name[len(name)-1].lower()) | ('national' in name[len(name)-1].lower()) | \
                            ('federal' in name[len(name)-1].lower()) | ('royal' in name[len(name)-1].lower()) | \
                                ('federate' in name[len(name)-1].lower()) | ('confederate' in name[len(name)-1].lower()):
                            type1.append('Government')
                            type2.append(' ')
                        elif ('international' in name[len(name)-1].lower()) | ('intergovernmental' in name[len(name)-1].lower()):
                            type1.append('International')
                            type2.append(' ')
                        else:
                            print(name[len(name)-1].lower())
                            type1.append('Other')
                            type2.append(' ')

                        type1Temp.append(str(type1[len(type1)-1]))
                        type2Temp.append(str(type2[len(type2)-1]))
                        cityTemp.append(str(city[len(city)-1]))

            type1Dist.append(type1Temp)
            type2Dist.append(type2Temp)
            cityDist.append(cityTemp)

            cityTemp = []
            tempOrgs = []
            type1Temp = []
            type2Temp = []

    return identifier, name, type1, type2, address, postalCode, city, state, country, type1Dist, type2Dist, cityDist


# this functions matches publications and authors through their identifiers
def papers_and_authors(DOIs):

    papersDOI = []
    authorsID = []

    for doi in tqdm(DOIs):

        try:
            # getting pubication's authors data
            authors = AbstractRetrieval(doi).authors

            for author in authors:
                # a publication's DOI is appended so much times as the numbers of its authors
                papersDOI.append(str(doi))
                # the first element in an author's list of information (author[0]) is Scopus author identifier
                authorsID.append(str(AuthorRetrieval(author[0]).identifier))

        except:
            continue

    return papersDOI, authorsID


# this functions matches publications and organizations through their identifiers
def papers_and_orgs(DOIs, orgID):

    pubsExport = []
    orgsExport = []

    for doi in tqdm(DOIs):

        try:
            tempOrgs = [str(org[0])
                        for org in AbstractRetrieval(doi).affiliation]
            for org in orgID:
                if (org in tempOrgs):
                    # a publication's DOI is appended so much times as the number of
                    # organizations affiliated to its authors
                    pubsExport.append(str(doi))
                    # the position of organization's ID in orgID[] list retrieved,
                    # so the coressponding name be appended in orgsExport[]
                    orgsExport.append(org)

            tempOrgs = []

        except:
            continue

    return pubsExport, orgsExport


# this function matches authors and organizations
def authors_and_organizations(DOIs):

    orgExport = []
    authorExport = []

    for doi in tqdm(DOIs):

        try:
            paperOrgs = [org[0] for org in AbstractRetrieval(doi).affiliation]
            authorsID = [AuthorRetrieval(
                author[0]).identifier for author in AbstractRetrieval(doi).authors]

            for authorID in authorsID:
                for org in AuthorRetrieval(authorID).affiliation_history:
                    if (org[0] in paperOrgs) | (org[1] in paperOrgs) & ((org[0] not in orgExport) | (authorID not in authorExport)):
                        orgExport.append(str(org[0]))
                        authorExport.append(str(authorID))
        except:
            continue

    return authorExport, orgExport
