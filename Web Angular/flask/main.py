from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def root():
    return 'Hello World'


@app.route('/search', methods=['GET', 'POST'])
def search():

    data = request.get_json()

    basicQuery = 'SELECT publications.DOI, publications.Year, publications.Citations_Count, ' + \
        'publications.Keywords, publications.Fields, authors.First_Name, authors.Last_Name, ' + \
        'authors.Subjected_Areas, authors.Citations_Count, organizations.Name, ' + \
        'organizations.Type_1, organizations.Type_2, organizations.City, organizations.Country ' + \
        'FROM ((((publications_authors ' + \
        'INNER JOIN publications ON publications_authors.DOI = publications.DOI) ' + \
        'INNER JOIN authors ON publications_authors.Author_ID = authors.ID) ' + \
        'INNER JOIN authors_organizations ON authors.ID = authors_organizations.Author_ID) ' + \
        'INNER JOIN organizations ON authors_organizations.Organization_ID = organizations.ID)\n'

    conditionQuery = 'WHERE\n'

    for key in data.keys():
        if ("keyword" in key) & (data[key] != None):
            tempQuery = f'`Keywords` LIKE \'%{data[key].lower()}%\'\n'
            conditionQuery = conditionQuery + tempQuery
        elif ("boolean" in key) & (data[key] != None):
            tempQuery = data[key] + ' '
            conditionQuery = conditionQuery + tempQuery
        elif key == "years1":
            tempQuery = f'AND `Year` >= {data[key]}\n'
            conditionQuery = conditionQuery + tempQuery
        elif key == "years2":
            tempQuery = f'AND `Year` <= {data[key]}\n'
            conditionQuery = conditionQuery + tempQuery
        elif data[key] == True:
            tempQuery = f'AND `Fields` LIKE \'%{key.lower()}%\'\n'
            conditionQuery = conditionQuery + tempQuery

    query = basicQuery + conditionQuery
    query = query[:-1] + ';'

    print(query)

    return '200'


if __name__ == '__main__':
    app.run(debug=True)
