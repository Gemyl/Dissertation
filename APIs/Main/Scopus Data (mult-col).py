from pybliometrics.scopus import AbstractRetrieval
from sqlalchemy import create_engine
from ScopusQuery import GetDOIs
import pandas as pd

####### VARIABLES #######
MaxAuthors = 0
#########################

##### LISTS & DICS ######
Row = {}
ColumnsNames =[]
#########################

#### SCOPUS SUBJECTS ####
['AGRI', 'ARTS', 'BIOC', 'BUSI', 'CENG', 'CHEM', 'COMP',
  'DECI', 'DENT', 'EART', 'ECON', 'ENER', 'ENGI', 'ENVI',
  'HEAL', 'IMMU', 'MATE', 'MATH', 'MEDI', 'NEUR', 'NURS',
  'PHAR', 'PHYS', 'PSYC', 'SOCI', 'VETE', 'MULT']
##########################

##### GETTING DOIs ######
Keywords = 'artificial intelligence'
Subjects = ['SOCI']
Years = '2022'
DOIs = GetDOIs( Keywords, Years, Subjects)
#########################

# FINDING MAX NUMBER OF A PAPER'S AUTHORS #
for i in range(len(DOIs)):
    if (len(AbstractRetrieval(DOIs[i]).authors) > MaxAuthors) & (len(AbstractRetrieval(DOIs[i]).authors) < 10):
        MaxAuthors = len(AbstractRetrieval(DOIs[i]).authors)
###########################################

## TABLE INITIALIZATION ##
ColumnsNames.append('DOI')
for i in range(MaxAuthors):
    ColumnsNames.append('Author ' + str(i+1) + ' ID')
    ColumnsNames.append('Author ' + str(i+1) + ' Name')

TableDF = pd.DataFrame(columns=ColumnsNames)
#########################

#### RETRIEVING DATA ####
for i in range(len(DOIs)):
    NumAuthors = len(AbstractRetrieval(DOIs[i]).authors)
    Row['DOI'] = str(DOIs[i])
    for j in range(MaxAuthors):
        if j < NumAuthors:
            Row['Author ' + str(j+1) + ' ID'] = [str(AbstractRetrieval(DOIs[i]).authors[j][0])]
            Row['Author ' + str(j+1) + ' Name'] = [AbstractRetrieval(DOIs[i]).authors[j][1]]
        else:
            Row['Author ' + str(j+1) + ' ID'] = [' ']
            Row['Author ' + str(j+1) + ' Name'] = [' ']
    
    RowDF = pd.DataFrame(Row)
    TableDF = pd.concat([TableDF, RowDF], axis = 0, ignore_index = True)
    Row = {}
#########################

# CONNECTION TO MySQL Server #
engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                       .format(user="root",
                               pw="gemyl",
                               db="george"))

TableDF.to_sql('demo1', con=engine, if_exists='append',chunksize=1000)
##############################