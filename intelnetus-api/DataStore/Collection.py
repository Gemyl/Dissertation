BLUE = "\033[1;34m"

RESET = "\033[0m"

MAX_COLUMN_SIZE = 5000

SCOPUS_FIELDS = ['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 
    'COMP','DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
    'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'MULT', 'NEUR', 'NURS', 
    'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE']

FULL_NAME_FIELDS = ["Agricultural and Biological Sciences", "Arts and Humanities", "Biochemistry Genetics and Molecular Biology", 
    "Business, Management, and Accounting", "Chemical Engineering", "Chemistry", "Computer Science", "Decision Sciences", 
    "Dentistry", "Earth and Planetary Sciences", "Economics, Econometrics and Finance", "Energy", "Engineering", 
    "Environmental Science", "Health Professions", "Immunology and Microbiology", "Materials Science", "Mathematics", "Medicine",
    "Multidisciplinary", "Neuroscience", "Nursing", "Pharmacology, Toxicology and Pharmaceutics","Physics and Astronomy", 
    "Psychology", "Social Sciences", "Veterinary"]
                      
COMMON_WORDS = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about',
    'to', 'from', 'in', 'on', 'up', 'out', 'as', 'into', 'through', 'over', 'after', 'under',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'has', 'had',
    'will', 'be', 'not', 'would', 'should', 'before', 'few', 'many', 'much', 'so', 'furthermore'] 

ORGANIZATIONS_TYPES_KEYWORDS = {
    "university": ['university', 'college', 'departement'],
    "academy": ['academy', 'academic', 'academia'],
    "school": ['school', 'faculty'],
    "research": ['research', 'researchers'],
    "business": ['inc', 'ltd', 'corporation'],
    "association": ['association'],
    "nonProfit": ['non-profit'],
    "government": ['government', 'gov', 'public', 'state', 'national', 'federal', 'federate', 'confederate', 'royal'],
    "international": ['international']
}

def get_scopus_fields(fieldsIds):
    returnedFields = []
    for id in fieldsIds:
        returnedFields.append(SCOPUS_FIELDS[int(id)])

    return returnedFields

def get_full_name_fields(fieldsIds):
    returnedFields = []
    for id in fieldsIds:
        returnedFields.append(FULL_NAME_FIELDS[int(id)])

    return returnedFields