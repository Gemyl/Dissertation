from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import OrderedDict
import mysql.connector as connector

connection = connector.connect(host='localhost',
                               port='3306',
                               user='root',
                               password='gemyl',
                               database='scopus',
                               auth_plugin='mysql_native_password')
cursor = connection.cursor()

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def root():
    return 'Hello World'


@app.route('/search', methods=['GET', 'POST'])
def search():

    keywords = request.args.getlist('keywords')[0].split(',')
    booleans = request.args.getlist('booleans')[0].split(',')
    fields = request.args.getlist('fields')[0].split(',')
    year1 = request.args.get("year1")
    year2 = request.args.get("year2")

    basicQuery = f'SELECT scopus_publications.DOI, scopus_publications.Year, scopus_publications.Citations_Count, \n' + \
        'scopus_publications.Keywords, scopus_publications.Fields, scopus_authors.First_Name, scopus_authors.Last_Name, \n' + \
        'scopus_authors.Fields_Of_Study, scopus_authors.Citations_Count, scopus_organizations.Name, \n' + \
        'scopus_organizations.Type_1, scopus_organizations.Type_2, scopus_organizations.City, scopus_organizations.Country \n' + \
        'FROM ((((scopus_publications_authors \n' + \
        'INNER JOIN scopus_publications ON scopus_publications_authors.Publication_ID = scopus_publications.ID) \n' + \
        'INNER JOIN scopus_authors ON scopus_publications_authors.Author_ID = scopus_authors.ID) \n' + \
        'INNER JOIN scopus_authors_organizations ON scopus_authors.ID = scopus_authors_organizations.Author_ID) \n' + \
        'INNER JOIN scopus_organizations ON scopus_authors_organizations.Organization_ID = scopus_organizations.ID)\n'

    conditionQuery = 'WHERE\n ('
    for i in range(len(keywords)):
        if (i == 0):
            tempQuery = f'`Keywords` LIKE \'%{keywords[i].lower()}%\'\n'
            conditionQuery = conditionQuery + tempQuery
        else:
            tempQuery = f'{booleans[i-1]} `Keywords` LIKE \'%{keywords[i].lower()}%\'\n'
            conditionQuery = conditionQuery + tempQuery
    conditionQuery = conditionQuery + ') \n AND \n'

    conditionQuery = conditionQuery + f'scopus_publications.Year >= {year1}\n'
    conditionQuery = conditionQuery + f'AND scopus_publications.Year <= {year2}\n AND \n (\n'
    for i in range(len(fields)):
        if (i == 0):
            tempQuery = f'`Fields` LIKE \'%{fields[i]}%\'\n'
            conditionQuery = conditionQuery + tempQuery
        else: 
            tempQuery = f'OR `Fields` LIKE \'%{fields[i]}%\'\n'
            conditionQuery = conditionQuery + tempQuery
    conditionQuery = conditionQuery + '\n );'
    
    query = basicQuery + conditionQuery

    result = []
    cursor.execute(query)
    for row in cursor:
        result.append({
            "publicationDoi":row[0],
            "publicationYear":row[1],
            "publicationCitationsCount":row[2],
            "publicationKeywords":row[3],
            "publicationFields":row[4],
            "authorFirstName":row[5],
            "authorLastName":row[6],
            "authorFieldsOfStudy":row[7],
            "authorCitationsCount":row[8],
            "organizationName":row[9],
            "organizationType1":row[10],
            "organizationType2":row[11],
            "organizationCity":row[12],
            "organizationCountry":row[13]
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
