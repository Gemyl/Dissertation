from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
from ScopusQuery import GetDOIs
import pandas as pd

####### VARIABLES #######
MaxAuthors = 0
#########################

######### LISTS #########
Table = []
Column = []
DOIs = []
Authors = []
AuthorsTemp = []
ColumnsNames =[]
Subjects = []
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

# FINDING MAX NUMBER OF A PAPER'S AUTHORS #
for i in range(len(DOIs)):
    if (len(AbstractRetrieval(DOIs[i]).authors) > MaxAuthors) & (len(AbstractRetrieval(DOIs[i]).authors) < 10):
        MaxAuthors = len(AbstractRetrieval(DOIs[i]).authors)
###########################################

##### COLUMNS NAMES #####
ColumnsNames.append('DOI')
for i in range(MaxAuthors):
    ColumnsNames.append('Author ' + str(i+1))
##########################

# TABLES INITIALIZATION ##
for i in range(len(DOIs)):
    for j in range(MaxAuthors+1):
        Column.append(' ')
    Table.append(Column)
    Column = []
##########################

#### INSERTING VALUES ####
for i in range(len(DOIs)):
    NumAuthors = len(AbstractRetrieval(DOIs[i]).authors)
    Table[i][0] = DOIs[i]
    for j in range(1, NumAuthors+1):
        Table[i][j] = str(AbstractRetrieval(DOIs[i]).authors[j-1][0])
##########################

#### EXTRACTING .XLSX ####
FinalTable = pd.DataFrame(Table, columns=ColumnsNames)
FinalTable.to_excel('Demo.xlsx')
##########################