from flask import Blueprint, render_template, request
from ScopusQuery import GetDOIs, GetMetadata, FormatKeywords
from MySQLserver import PushDataFrame

SearchPage = Blueprint('SearchPage', __name__)

@SearchPage.route('/search', methods = ['GET', 'POST'])
def search():
    
    if request.method == 'POST':
        subjects = []       
        keywords = request.form.get('keywords')
        yearsRange = request.form.get('years-range')
        subjects = request.form.get('subjects')
        
        subjects = subjects.split(', ')
        keywords = FormatKeywords(keywords=keywords)
        
        print(keywords)
        print(yearsRange)
        print(subjects)
        DOIs = GetDOIs(keywords=keywords, yearsRange=yearsRange, subjects=subjects)
        dataFrame = GetMetadata(DOIs=DOIs)
        PushDataFrame(dataFrame=dataFrame)

    return render_template('search.html')