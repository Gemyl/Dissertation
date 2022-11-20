from flask import Blueprint, render_template

SearchPage = Blueprint('SearchPage', __name__)

@SearchPage.route('/search')
def search():
    return render_template('search.html')