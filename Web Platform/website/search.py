from flask import Blueprint, render_template, request
from pybliometrics.scopus import AbstractRetrieval
from sqlalchemy import create_engine
from ScopusQuery import GetDOIs
import pandas as pd

SearchPage = Blueprint('SearchPage', __name__)

@SearchPage.route('/search', methods = ['GET', 'POST'])
def search():
    
    if request.method == 'POST':
        
        MaxAuthors = 0
        
        Row = {}
        ColumnsNames =[]
        subjects = []

        user = request.form.get('user')
        password = request.form.get('password')
        database = request.form.get('database')
        keywords = request.form.get('keywords')
        yearsRange = request.form.get('years-range')
        subjects.append(request.form.get('subjects'))

        print(type(keywords))
        print(type(yearsRange))
        print(type(subjects))

        DOIs = GetDOIs(Keywords=keywords, YearsRange=yearsRange, Subjects=subjects)

        for i in range(len(DOIs)):
            if (len(AbstractRetrieval(DOIs[i]).authors) > MaxAuthors) & (len(AbstractRetrieval(DOIs[i]).authors) < 10):
                MaxAuthors = len(AbstractRetrieval(DOIs[i]).authors)

        
        ColumnsNames.append('DOI')
        for i in range(MaxAuthors):
            ColumnsNames.append('Author ' + str(i+1) + ' ID')
            ColumnsNames.append('Author ' + str(i+1) + ' Name')

        TableDF = pd.DataFrame(columns=ColumnsNames)


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

        engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                        .format(user=user,
                                pw=password,
                                db=database))

        TableDF.to_sql('demo1', con=engine, if_exists='append',chunksize=1000)

    return render_template('search.html')