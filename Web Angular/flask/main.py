from flask import Flask, render_template, Blueprint, request, redirect, url_for

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    return 'Hello World'


@app.route('/search', methods=['GET', 'POST'])
def search():

    form = list(request.form.items())

    selectionQuery = 'SELECT publications.DOI, publications.Year, publications.Citations_Count, publications.Publisher, ' + \
        'publications.Authorship_Keywords, publications.Fields, authors.First_Name, authors.Last_Name, ' + \
        'authors.Subjected_Areas, authors.Item_Citations_Count, authors.Documents_Count, organizations.Name, ' + \
        'organizations.`Type (1)`, organizations.`Type (2)`, organizations.City, organizations.Region, organizations.Country ' + \
        'FROM ((((publications_authors ' + \
        'INNER JOIN publications ON publications_authors.DOI = publications.DOI) ' + \
        'INNER JOIN authors ON publications_authors.Author_ID = authors.ID) ' + \
        'INNER JOIN authors_organizations ON authors.ID = authors_organizations.Author_ID) ' + \
        'INNER JOIN organizations ON authors_organizations.Organization_ID = organizations.ID)\n'

    conditionQuery = 'WHERE\n'

    for field in form:
        if 'boolean' in field[0]:
            appendQuery = field[1]
            conditionQuery = conditionQuery + appendQuery + ' '
        elif (field[0] == 'years1'):
            appendQuery = f'AND `Year` >= {field[1]}\n'
            conditionQuery = conditionQuery + appendQuery
        elif (field[0] == 'years2'):
            appendQuery = f'AND `Year` <= {field[1]}\n'
            conditionQuery = conditionQuery + appendQuery
        elif 'keywords' in field[0]:
            appendQuery = f'Authorship_Keywords LIKE \'%{field[1].lower()}%\'\n'
            conditionQuery = conditionQuery + appendQuery
        else:
            appendQuery = f'AND `Fields` LIKE \'%{field[1].lower()}%\'\n'
            conditionQuery = conditionQuery + appendQuery

    query = selectionQuery + conditionQuery
    query = query[:-1] + ';'

    print(query)

    return '200'


if __name__ == '__main__':
    app.run(debug=True)
