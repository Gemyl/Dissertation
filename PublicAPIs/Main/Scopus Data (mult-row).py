from pybliometrics.scopus import AbstractRetrieval
from ScopusQuery import GetDOIs
import pandas as pd

####### VARIABLES #######
MaxAuthors = 0
#########################

##### LISTS & DICS ######
Row = {}
DOIs = []
Table = []
Column = []
Authors = []
Subjects = []
AuthorsTemp = []
ColumnsNames =[]
#########################

#### SCOPUS SUBJECTS ####
['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
  'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
  'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
  'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']
##########################

##### GETTING DOIs ######
Subjects = ['SOCI']
DOIs = GetDOIs(DOIs,Subjects)
#########################

## TABLE INITIALIZATION ##
ColumnsNames.append('DOI')
ColumnsNames.append('Author ID')
ColumnsNames.append('Author Name')
TableDF = pd.DataFrame(columns=ColumnsNames)
#########################

#### RETRIEVING DATA ####
for i in range(len(DOIs)):
    NumAuthors = len(AbstractRetrieval(DOIs[i]).authors)
    for j in range(NumAuthors):

        Row['DOI'] = str(DOIs[i])
        Row['Author ID'] = [str(AbstractRetrieval(DOIs[i]).authors[j][0])]
        Row['Author Name'] = [AbstractRetrieval(DOIs[i]).authors[j][1]]
        RowDF = pd.DataFrame(Row)
        TableDF = pd.concat([TableDF, RowDF], axis = 0, ignore_index = True)
        Row = {}

TableDF.to_excel('Demo(mult-row).xlsx')
#########################