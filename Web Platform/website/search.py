from flask import Blueprint, render_template, request
from ScopusQuery import GetDOIs, GetMetadata
from MySQLserver import PushDataFrame

SearchPage = Blueprint('SearchPage', __name__)

@SearchPage.route('/search', methods = ['GET', 'POST'])
def search():
    
    if request.method == 'POST':
        subjects = []       
        user = request.form.get('user')
        password = request.form.get('password')
        database = request.form.get('database')
        keywords = request.form.get('keywords')
        yearsRange = request.form.get('years-range')
        subjects.append(request.form.get('subjects'))

        DOIs = GetDOIs(Keywords=keywords, YearsRange=yearsRange, Subjects=subjects)
        dataFrame = GetMetadata(DOIs=DOIs)
        PushDataFrame(user=user, password=password, database=database, dataFrame=dataFrame)

    return render_template('search.html')