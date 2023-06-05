def getKeywords():
    return 'artificial intelligence, machine learning, learning algorithm, deep learning, pattern recognition'

def getYear():
    return '2021'

def getScopusFields(fieldsIds):
    scopusFields = ['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
          'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
          'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
          'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']
    
    returnedFields = []
    for id in fieldsIds:
        returnedFields.append(scopusFields[int(id)])

    return returnedFields

def getFullNameFields(fieldsIds):
    fullNameFields = ["Agricultural and Biological Sciences", "Arts and Humanities", "Biochemistry Genetics and Molecular Biology", "Business, Management, and Accounting",
                      "Chemical Engineering", "Chemistry", "Computer Science", "Decision Sciences", "Dentistry", "Earth and Planetary Sciences", "Economics, Econometrics and Finance", 
                      "Energy", "Engineering", "Environmental Science", "Health Professions", "Immunology and Microbiology", "Materials Science", "Mathematics", "Medicine",
                      "Multidisciplinary", "Neuroscience", "Nursing", "Pharmacology, Toxicology and Pharmaceutics","Physics and Astronomy", "Psychology", "Social Sciences", "Veterinary"]
    
    returnedFields = []
    for id in fieldsIds:
        returnedFields.append(fullNameFields[int(id)])

    return returnedFields

def getCommonWords():
    return ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about',
            'to', 'from', 'in', 'on', 'up', 'out', 'as', 'into', 'through', 'over', 'after', 'under',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'has', 'had',
            'will', 'be', 'not', 'would', 'should', 'before', 'few', 'many', 'much', 'so', 'furthermore']