from flask import Blueprint, render_template, request

SearchPage = Blueprint('SearchPage', __name__)

@SearchPage.route('/search', methods = ['GET', 'POST'])
def search():
    data = request.form

    for key in data.keys():
        print(data[key])
    return render_template('search.html')