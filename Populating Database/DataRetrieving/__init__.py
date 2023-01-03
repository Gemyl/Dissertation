from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval, AuthorSearch
from TextFormating import format_keywords, list_to_string
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
def papers_data(DOIs, keywords):

    # each list corresponds to a paper's attribute
    DOI = []
    year = []
    title = []
    journal = []
    subjects = []
    userKeywords = []
    citationsCount = []
    authorshipKeywords = []
    
    # in this loop every DOI is accessed
    # each DOI represents a paper
    for i in range(len(DOIs)):

        paperInfo = AbstractRetrieval(DOIs[i], view='FULL')

        # paper's year
        try:
            year.append(str(paperInfo.confdate[0][0]))
        except:
            year.append(' ')
        
        # paper's DOI
        try:    
            DOI.append(str(DOIs[i]))
        except:
            DOI.append(' ')

        # keywords given by user
        try:    
            userKeywords.append(keywords)
        except:
            userKeywords.append(' ')

        # paper's journal
        try:
            journal.append(str(paperInfo.publisher))
        except:
            journal.append(' ')

        # paper's title
        try:
            title.append(paperInfo.title)
        except:
            title.append(' ')

        # paper's number of citations
        try:
            citationsCount.append(paperInfo.citedby_count)
        except:
            citationsCount.append(' ')

        # paper's referenced subjected areas
        try:
            subjects.append(', '.join(str(sub[0]) for sub in paperInfo.subject_areas))
        except:
            subjects.append(' ')

        # keywords given by paper's authors
        try:    
            authorshipKeywords.append(list_to_string(paperInfo.authkeywords))
        except:
            authorshipKeywords.append(' ')

    return DOI, year, journal, authorshipKeywords, userKeywords, subjects, title, citationsCount 


# this function retrieves the authors data from Scopus
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
    for i in range(len(DOIs)):

        # getting a paper's authors
        authors = AbstractRetrieval(DOIs[i]).authors

        # in this loop every author is accessed
        for author in authors:

            # getting all the available information for each author
            authorInfo = AuthorRetrieval(author[0])

            # checking if an author has been already accesed during this search
            if identifier.count(authorInfo.identifier) == 0:                   

                # author's Scopus ID
                try:
                    identifier.append(str(authorInfo.identifier))
                except:
                    identifier.append(' ')

                # author's first name
                try:
                    firstName.append(authorInfo.given_name)
                except:
                    firstName.append(' ')

                # author's last name
                try:
                    lastName.append(authorInfo.surname)
                except:
                    firstName.append(' ')

                # author's name as is indexed in Scopus
                try:
                    indexedName.append(str(authorInfo.indexed_name))
                except:
                    indexedName.append(' ')

                # author's referenced subjected areas
                try:
                    subjectedAreas.append(', '.join(str(sub[0]) for sub in authorInfo.subject_areas))
                except:
                    subjectedAreas.append('')  

                # author's h-index
                try:
                    hIndex.append(str(authorInfo.h_index))
                except:
                    hIndex.append(' ')

                # author's number of citations in items (e.g. papers)
                try:
                    itemCitations.append(str(authorInfo.citation_count))
                except:
                    itemCitations.append(' ')

                # author's number of citations made by other authors
                try:
                    authorsCitations.append(str(authorInfo.cited_by_count))
                except:
                    authorsCitations.append(' ')

                # number of documents authored
                try:
                    documentsCount.append(str(authorInfo.document_count))
                except:
                    documentsCount.append(' ')

    return identifier, firstName, lastName, subjectedAreas, hIndex, \
        itemCitations, authorsCitations, documentsCount 


# this function retrieves orgnizations data from Scopus
def orgs_data(DOIs):

    # each list corresponds to an organization's attribute
    name = []
    city = []
    type = []
    state = []
    country = []
    address = []
    parentID = []
    parentName = []    
    postalCode = []
    identifier = []

    # in this loop every DOI is accessed
    for DOI in DOIs:
        tempOrgs = AbstractRetrieval(DOI).affiliation
        for org in tempOrgs:
            if org not in identifier:
                identifier.append(org[0])
                parentID.append('None')
                parentName.append('None')
        
        authors = AbstractRetrieval(DOI).authors
        for author in authors:
            authorID = author[0]
            for org in AuthorRetrieval(authorID).affiliation_current:
                if (org[0] not in identifier) & (org[1] in identifier):
                    identifier.append(org[0])
                    parentID.append(str(org[1]))
                    parentName.append(org[6])
                    
            for org in AuthorRetrieval(authorID).affiliation_history:
                if (org[0] not in identifier) & (org[1] in identifier):
                    identifier.append(org[0])
                    parentID.append(str(org[1]))
                    parentName.append(org[6])

    # getting all organizations that are affiliated in each paper
    for orgID in identifier:

        orgInfo = AffiliationRetrieval(orgID)

        # organization's name
        try:
            name.append(str(orgInfo.affiliation_name))
        except:
            name.append(' ')

        # organization's type (e.g. university, college)
        try:
            type.append(str(orgInfo.org_type))
        except:
            type.append(' ')

        # organization's address
        try:
            address.append(str(orgInfo.address))
        except:
            address.append(' ')
        
        # organization's postal code
        try:
            postalCode.append(str(orgInfo.postal_code))
        except:
            postalCode.append(' ')

        # organization's city
        try:
            city.append(str(orgInfo.city))
        except:
            city.append(' ')

        # organization's state or region
        try:
            state.append(str(orgInfo.state))
        except:
            state.append(' ')

        # organization's country
        try:
            country.append(str(orgInfo.country))
        except:
            country.append(' ')

    return identifier, name, type, address, postalCode, city, state, country, parentID, parentName


# this functions matches publications and authors through their identifiers
def papers_and_authors(DOIs):

    papersDOI = []
    authorsID = []

    for i in range(len(DOIs)):

        # checking if a publication has been already accessed
        if papersDOI.count(DOIs[i]) == 0:

            # getting publication's info
            paperInfo = AbstractRetrieval(DOIs[i])

            # getting pubication's authors data
            authors = paperInfo.authors

            for author in authors:

                # a publication's DOI is appended so much times as the numbers of its authors
                papersDOI.append(str(DOIs[i]))

                # the first element in an author's list of information (author[0]) is Scopus author identifier
                authorsID.append(str(author[0]))
    
    return papersDOI, authorsID


# this functions matches publications and organizations through their identifiers
def papers_and_orgs(DOIs):

    papersDOI = []
    orgsID = []

    for i in range(len(DOIs)):
        # checking if a publication has been already accessed
        if papersDOI.count(DOIs[i]) == 0:
            # getting publication's info
            paperInfo = AbstractRetrieval(DOIs[i])

            # getting publication's organizations data
            orgs = paperInfo.affiliation

            for org in orgs:
                # a publication's DOI is appended so much times as the number of
                # organizations affiliated to its authors
                papersDOI.append(str(DOIs[i]))

                # the first element in an organization's list of information (org[0]) is
                # Scopus organization identifier
                orgsID.append(str(org[0]))
        
    return papersDOI, orgsID


# this function matches authors and organizations
def authors_and_organizations(DOIs):

    orgsID = []
    paperOrgs = []
    authorsID = []
    isCurrentOrg = []
    totalOrgs = []
    formerOrgs = []
    
    for DOI in DOIs:
        # accessing each author's info for a given publication
        for author in AbstractRetrieval(DOI).authors:
            # checking if the author has any affiliation for the specific publication
            if author[4] != None:
                # organziations from author's affiliation that are related to the publication
                paperOrgs = [int(org) for org in author[4].split(';')]
                # current organizations
                currentOrgs = [org for org in AuthorRetrieval(author[0]).affiliation_current]
                # total organizations 
                totalOrgs = [org for org in AuthorRetrieval(author[0]).affiliation_history]
                # removing current from total organizations list to get the former orgnizations
                formerOrgs = [org for org in totalOrgs if org not in currentOrgs]
                
                for org in currentOrgs:
                    # checking if any organization (org[0]) or its parent (org[1], if exists) from author's current affiliation,
                    # is included in publication's related organizations
                    if (org[0] in paperOrgs) | (org[1] in paperOrgs):
                        # 'Yes' is appended in isCurrentOrg list to state that the specific organization is
                        # currently affiliated to the author
                        isCurrentOrg.append('Yes')
                        # both the ID of author and organizations are inserted in the corresponding lists
                        orgsID.append(str(org[0]))
                        authorsID.append(str(author[0]))

                # checking if any organization (or its parent) from author's former affiliation, 
                # is included in publication's related organizations
                for org in formerOrgs:
                    if (org[0] in paperOrgs) | (org[1] in paperOrgs):
                        # the organizations in this list belong to former affiliations,
                        # so 'No' is appended in isCurrentOrg list
                        isCurrentOrg.append('No')
                        # insertion of both author's and organization's ID
                        orgsID.append(str(org[0]))                    
                        authorsID.append(str(author[0]))      
            
                # reseting the list which contains each paper's related organizations
                paperOrgs = []
    
    return authorsID, orgsID, isCurrentOrg