from Preprocessing.Methods import applySqlSyntax, removeCommonWords, getSafeAttribute
from pybliometrics.scopus import PlumXMetrics
import uuid

university = ['university', 'college', 'departement']
academy = ['academy', 'academic', 'academia']
school = ['school', 'faculty']
research = ['research', 'researchers']
bussiness = ['inc', 'ltd', 'corporation']
association = ['association']
nonProfit = ['non-profit']
government = ['government', 'gov', 'public', 'state', 'national', 'federal', 'federate', 'confederate', 'royal']
international = ['international']

class Publication:
    def __init__(self, publicationInfo, year, doi):
        self.id = str(uuid.uuid4())
        self.doi = doi
        self.year = year
        self.title = applySqlSyntax(getSafeAttribute(publicationInfo, 'title', 'string'))
        self.journal = applySqlSyntax(getSafeAttribute(publicationInfo, 'publicationName', 'string'))
        self.abstract = applySqlSyntax(removeCommonWords(
            Publication.getAbstract(
                getSafeAttribute(publicationInfo, 'abstract', 'string'),
                getSafeAttribute(publicationInfo, 'description', 'string')
            )
        ))
        self.keywords = applySqlSyntax(Publication.getKeywords(getSafeAttribute(publicationInfo, 'authkeywords', 'string')))
        self.fields = applySqlSyntax(Publication.getFields(getSafeAttribute(publicationInfo, 'subject_areas', 'string')))
        self.citationsCount = Publication.getMaximumCitationsCount(
            getSafeAttribute(publicationInfo, 'citedby_count', 'number'),
            doi
        )
        self.authorsNumber = Publication.getAuthorsNumber(getSafeAttribute(publicationInfo, 'authors', 'list'))
        self.affiliationsNumber = Publication.getAffiliationsNumber(getSafeAttribute(publicationInfo, 'affiliation', 'list'))

    def getAbstract(abstract, description):
        if abstract != None:
            return applySqlSyntax(abstract)
        elif description != None:
            return applySqlSyntax(description)
        else:
            return "-"
        
    def getKeywords(keywords):
        if keywords != None:
            return applySqlSyntax(", ".join([keyword for keyword in keywords]))
        else:
            return "-"
    
    def getFields(fields):
        if fields != None:
            return applySqlSyntax(", ".join([field[0].lower() for field in fields]))
        else:
            return "-"
    
    def getMaximumCitationsCount(citationsCount, doi):
        maxCitations = citationsCount
        plumxCitations = PlumXMetrics(doi, id_type='doi').citation

        if plumxCitations != None:
            if maxCitations != 999999:
                plumxCitations = max([citation[1] for citation in plumxCitations])
                maxCitations = max(maxCitations, plumxCitations)
            else:
                maxCitations = max([citation[1] for citation in plumxCitations])

        return maxCitations
    
    def getAuthorsNumber(authors):
        if ((authors == "-") | (authors == None)):
            return 0
        
        return len(authors)
    
    def getAffiliationsNumber(affiliations):
        if ((affiliations == "-") | (affiliations == None)):
            return 0

        return len(affiliations)
    

class Author:
    def __init__(self,authorInfo):
        self.id = str(uuid.uuid4())
        self.scopusId = str(getSafeAttribute(authorInfo, 'identifier', 'string'))
        self.orcidId = getSafeAttribute(authorInfo, 'orcid', 'string')
        self.firstName = applySqlSyntax(getSafeAttribute(authorInfo, 'given_name', 'string'))
        self.lastName = applySqlSyntax(getSafeAttribute(authorInfo, 'surname', 'string'))
        self.hIndex = getSafeAttribute(authorInfo, 'h_index', 'number')
        self.fieldsOfStudy = applySqlSyntax(Author.getFields(getSafeAttribute(authorInfo, 'subject_areas', 'string')))
        self.citationsCount = getSafeAttribute(authorInfo, 'cited_by_count', 'number')
        self.affiliations = applySqlSyntax(Author.getAffiliations(getSafeAttribute(authorInfo, 'affiliation_history', 'string')))

    def getAffiliations(affiliationsInput):
        if ((affiliationsInput == "-") | (affiliationsInput == None)):
            return "-"

        affilHistory = []
        for affil in affiliationsInput:
            if ((affil.preferred_name not in affilHistory) & (affil.preferred_name != None)):
                if (affil.parent == None):
                    affilHistory.append(affil.preferred_name)
                else:
                    affilHistory.append(affil.preferred_name + ' - ' + affil.parent_preferred_name)
                    affilHistory.append(affil.parent_preferred_name)

        affilHistoryStr = ', '.join(affilHistory).replace("\'", " ")
        return applySqlSyntax(affilHistoryStr)
    
    def getFields(fields):
        if (fields == "-") | (fields == None):
            return "-"
        
        return applySqlSyntax(", ".join([field[0].lower() for field in fields]))
        

class Organization:
    def __init__(self, organizationInfo):
        self.id = str(uuid.uuid4())
        self.scopusId = str(getSafeAttribute(organizationInfo, 'identifier', 'string'))
        self.name = applySqlSyntax(getSafeAttribute(organizationInfo, 'affiliation_name', 'string'))
        self.type1, self.type2 = Organization.getAffiliationTypes(organizationInfo)
        self.address = applySqlSyntax(getSafeAttribute(organizationInfo, 'address', 'string'))
        self.city = applySqlSyntax(getSafeAttribute(organizationInfo, 'city', 'string'))
        self.country = applySqlSyntax(getSafeAttribute(organizationInfo, 'country', 'string'))

    def getAffiliationTypes(affiliationObj):
        type = getSafeAttribute(affiliationObj, 'org_type', 'string')
        name = getSafeAttribute(affiliationObj, 'affiliation_name', 'string')

        if (type == 'univ') | (type == 'coll') | \
                (len([univ for univ in university if univ in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'University - College'

        elif (type == 'sch') | \
                (len([sch for sch in school if sch in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'School'

        elif (type == 'res') | \
                (len([acad for acad in academy if acad in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'Research Institute'

        elif (type == 'gov') | \
                (len([gov for gov in government if gov in name.lower()]) > 0):
            type1 = 'Government'
            type2 = ' '

        elif (type == 'assn') | \
                (len([assn for assn in association if assn in name.lower()]) > 0):
            type1 = 'Association'
            type2 = ' '

        elif (type == 'corp') | \
                (len([bus for bus in bussiness if bus in name.lower()]) > 0):
            type1 = 'Business'
            type2 = ' '

        elif (type == 'non') | \
                (len([np for np in nonProfit if np in name.lower()]) > 0):
            type1 = 'Non-profit'
            type2 = ' '

        else:
            type1 = "Other"
            type2 = "Other"

        return type1, type2