from flask import Blueprint, render_template, request
from insert2mysql import connect_to_MySQL, commit_and_close

SearchPage = Blueprint('SearchPage', __name__)

@SearchPage.route('/search', methods = ['GET', 'POST'])
def search():

    if request.method == 'POST':
        con, cur, error = connect_to_MySQL('gemyl')
        query = 'SELECT publications.DOI, publications.Year, publications.Citations_Count, publications.Publisher, ' + \
            'publications.Authorship_Keywords, publications.Fields, authors.First_Name, authors.Last_Name, ' + \
            'authors.Subjected_Areas, authors.Item_Citations_Count, authors.Documents_Count, organizations.Name, ' + \
            'organizations.`Type (1)`, organizations.`Type (2)`, organizations.City, organizations.Region, organizations.Country ' + \
            'FROM ((((publications_authors ' + \
            'INNER JOIN publications ON publications_authors.DOI = publications.DOI) ' + \
            'INNER JOIN authors ON publications_authors.Author_ID = authors.ID) ' + \
            'INNER JOIN authors_organizations ON authors.ID = authors_organizations.Author_ID) ' + \
            'INNER JOIN organizations ON authors_organizations.Organization_ID = organizations.ID);'
        cur.execute(query)
        publications = cur.fetchall()

        query = 'SELECT * FROM cultural_distances;'
        cur.execute(query)
        distances = cur.fetchall()

        commit_and_close(con, cur)
        return render_template('display.html', pubs = publications, dists = distances)

    return render_template('search.html')