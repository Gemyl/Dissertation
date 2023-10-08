from DataCleaner.Services import get_sql_syntax, remove_common_words, get_safe_attribute
from DataStore.Collection import COMMON_WORDS, MAX_COLUMN_SIZE, ORGANIZATIONS_TYPES_KEYWORDS
from pybliometrics.scopus import PlumXMetrics
import uuid

class Publication:
    def __init__(self, publication_data, year, doi):
        self.id = str(uuid.uuid4())
        self.doi = doi
        self.year = year
        self.title = get_sql_syntax(
            get_safe_attribute(publication_data, 'title', 'string')
        )
        
        self.journal = get_sql_syntax(
            get_safe_attribute(publication_data, 'publicationName', 'string')
        )
        
        self.abstract = get_sql_syntax(
            remove_common_words(
                Publication.get_abstract(
                    get_safe_attribute(publication_data, 'abstract', 'string'),
                    get_safe_attribute(publication_data, 'description', 'string')
                ),
                COMMON_WORDS
            )
        )
        
        self.keywords = get_sql_syntax(
            Publication.get_keywords(
                get_safe_attribute(publication_data, 'authkeywords', 'string')
            )
        )
        
        self.fields = get_sql_syntax(
            Publication.get_fields(
                get_safe_attribute(publication_data, 'subject_areas', 'string')
            )
        )
        
        self.fields_abbreviations = get_sql_syntax(
            Publication.get_fields_abbreviations(
                get_safe_attribute(publication_data, 'subject_areas', 'string')
            )
        )
        
        self.citations_count = Publication.get_maximum_citations_count(
            get_safe_attribute(publication_data, 'citedby_count', 'number'),
            doi
        )
        
        self.authors_number = Publication.get_authors_number(
            get_safe_attribute(publication_data, 'authors', 'list')
        )
        
        self.affiliations_number = Publication.get_affiliations_number(
            get_safe_attribute(publication_data, 'affiliation', 'list')
        )

    def get_abstract(abstract, description):
        if abstract != None:
            item = get_sql_syntax(abstract)
        
        elif description != None:
            item = get_sql_syntax(description)
        
        else:
            item = "-"

        if (len(item) > MAX_COLUMN_SIZE):
            item = item[:MAX_COLUMN_SIZE]

        return item
        
    def get_keywords(keywords):
        if keywords != None:
            item = get_sql_syntax(", ".join([keyword for keyword in keywords]))
        else:
            item = "-"

        if (len(item) > MAX_COLUMN_SIZE):
            item = item[:MAX_COLUMN_SIZE]

        return item
    
    def get_fields(fields):
        if fields != None:
            item = get_sql_syntax(", ".join([field[0].lower() for field in fields]))
        else:
            item = "-"

        if (len(item) > MAX_COLUMN_SIZE):
            item = item[:MAX_COLUMN_SIZE]

        return item
        
    def get_fields_abbreviations(fields):
        if fields != None:
            return get_sql_syntax(", ".join([field[1].lower() for field in fields]))
        else:
            return "-"
    
    def get_maximum_citations_count(citations_count, doi):
        max_citations = citations_count
        plumx_citations = PlumXMetrics(doi, id_type='doi').citation

        if plumx_citations != None:
            if max_citations != 999999:
                plumx_citations = max([citation[1] for citation in plumx_citations])
                max_citations = max(max_citations, plumx_citations)
            else:
                max_citations = max([citation[1] for citation in plumx_citations])

        return max_citations
    
    def get_authors_number(authors):
        if ((authors == "-") | (authors == None)):
            return 0
        
        return len(authors)
    
    def get_affiliations_number(affiliations):
        if ((affiliations == "-") | (affiliations == None)):
            return 0

        return len(affiliations)
    

class Author:
    def __init__(self,author_data):
        self.id = str(uuid.uuid4())
        self.scopus_id = str(get_safe_attribute(author_data, 'identifier', 'string'))
        self.orcid_id = get_safe_attribute(author_data, 'orcid', 'string')
        self.first_name = get_sql_syntax(
            get_safe_attribute(author_data, 'given_name', 'string')
        )
        
        self.last_name = get_sql_syntax(
            get_safe_attribute(author_data, 'surname', 'string')
        )
        
        self.h_index = get_safe_attribute(author_data, 'h_index', 'number')
        self.fields_of_study = get_sql_syntax(
            Author.get_fields(get_safe_attribute(author_data, 'subject_areas', 'string'))
        )
        
        self.citations_count = get_safe_attribute(author_data, 'cited_by_count', 'number')
        self.affiliations = get_sql_syntax(
            Author.get_affiliations(get_safe_attribute(author_data, 'affiliation_history', 'string'))
        )

    def get_affiliations(affiliations):
        if ((affiliations == "-") | (affiliations == None)):
            return "-"

        affiliations_history = []
        for affiliation in affiliations:
            if ((affiliation.preferred_name not in affiliations_history) & (affiliation.preferred_name != None)):
                if (affiliation.parent == None):
                    affiliations_history.append(affiliation.preferred_name)
                else:
                    affiliations_history.append(affiliation.preferred_name + ' - ' + affiliation.parent_preferred_name)
                    affiliations_history.append(affiliation.parent_preferred_name)

        affiliations_history_str = ', '.join(affiliations_history).replace("\'", " ")
        if (len(affiliations_history_str) > MAX_COLUMN_SIZE):
            affiliations_history_str = affiliations_history_str[:MAX_COLUMN_SIZE]
        
        affiliations_history_str = get_sql_syntax(affiliations_history_str)

        return affiliations_history_str
    
    def get_fields(fields):
        if (fields == "-") | (fields == None):
            return "-"
        
        fields_str = ", ".join([field[0].lower() for field in fields])
        if (len(fields_str) > MAX_COLUMN_SIZE):
            fields_str = fields_str[:MAX_COLUMN_SIZE]

        fields_str = get_sql_syntax(fields_str)
        
        return fields_str
        

class Organization:
    def __init__(self, organization_data):
        self.id = str(uuid.uuid4())
        self.scopus_id = str(get_safe_attribute(organization_data, 'identifier', 'string'))
        self.name = get_sql_syntax(
            get_safe_attribute(organization_data, 'affiliation_name', 'string')
        )
        
        self.type_1, self.type_2 = Organization.get_affiliation_types(organization_data)
        self.address = get_sql_syntax(
            get_safe_attribute(organization_data, 'address', 'string')
        )
        
        self.city = get_sql_syntax(
            get_safe_attribute(organization_data, 'city', 'string')
        )
        
        self.country = get_sql_syntax(
            get_safe_attribute(organization_data, 'country', 'string')
        )

    def get_affiliation_types(affiliation_record):
        type = get_safe_attribute(affiliation_record, 'org_type', 'string')
        name = get_safe_attribute(affiliation_record, 'affiliation_name', 'string')

        if (type == 'univ') | (type == 'coll') | \
                (len([univ for univ in ORGANIZATIONS_TYPES_KEYWORDS['university'] if univ in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'University - College'

        elif (type == 'sch') | \
                (len([sch for sch in ORGANIZATIONS_TYPES_KEYWORDS['school'] if sch in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'School'

        elif (type == 'res') | \
                (len([acad for acad in ORGANIZATIONS_TYPES_KEYWORDS['academy'] if acad in name.lower()]) > 0):
            type1 = 'Academic'
            type2 = 'Research Institute'

        elif (type == 'gov') | \
                (len([gov for gov in ORGANIZATIONS_TYPES_KEYWORDS['government'] if gov in name.lower()]) > 0):
            type1 = 'Government'
            type2 = ' '

        elif (type == 'assn') | \
                (len([assn for assn in ORGANIZATIONS_TYPES_KEYWORDS['association'] if assn in name.lower()]) > 0):
            type1 = 'Association'
            type2 = ' '

        elif (type == 'corp') | \
                (len([bus for bus in ORGANIZATIONS_TYPES_KEYWORDS['business'] if bus in name.lower()]) > 0):
            type1 = 'Business'
            type2 = ' '

        elif (type == 'non') | \
                (len([np for np in ORGANIZATIONS_TYPES_KEYWORDS['non-proit'] if np in name.lower()]) > 0):
            type1 = 'Non-profit'
            type2 = ' '

        else:
            type1 = "Other"
            type2 = "Other"

        return type1, type2