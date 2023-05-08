from flask import Flask, request, jsonify
from flask_cors import CORS
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

    keywords = [value for key, value in request.args.items() if "keyword" in key.lower()]
    booleans = [value for key, value in request.args.items() if "boolean" in key.lower()]
    year1 = request.args.get("years1")
    year2 = request.args.get("years2")
    subjects = [key.lower() for key, value in request.args.items() if value == 'true']

    basicQuery = f'SELECT scopus_publications.DOI, scopus_publications.Year, scopus_publications.Citations_Count, ' + \
        'scopus_publications.Keywords, scopus_publications.Fields, scopus_authors.First_Name, scopus_authors.Last_Name, ' + \
        'scopus_authors.Fields_Of_Study, scopus_authors.Citations_Count, scopus_organizations.Name, ' + \
        'scopus_organizations.Type_1, scopus_organizations.Type_2, scopus_organizations.City, scopus_organizations.Country ' + \
        'FROM ((((scopus_publications_authors ' + \
        'INNER JOIN scopus_publications ON scopus_publications_authors.Publication_ID = scopus_publications.ID) ' + \
        'INNER JOIN scopus_authors ON scopus_publications_authors.Author_ID = scopus_authors.ID) ' + \
        'INNER JOIN scopus_authors_organizations ON scopus_authors.ID = scopus_authors_organizations.Author_ID) ' + \
        'INNER JOIN scopus_organizations ON scopus_authors_organizations.Organization_ID = scopus_organizations.ID)\n'

    conditionQuery = 'WHERE\n'
    for i in range(len(keywords)):
        if (i == 0):
            tempQuery = f'`Keywords` LIKE \'%{keywords[i].lower()}%\'\n'
            conditionQuery = conditionQuery + tempQuery
        else:
            tempQuery = f'{booleans[i-1]} `Keywords` LIKE \'%{keywords[i].lower()}%\'\n'

    conditionQuery = conditionQuery + f'AND scopus_publications.Year >= {year1}\n'
    conditionQuery = conditionQuery + f'AND scopus_publications.Year <= {year2}\n'

    for subj in subjects:
        tempQuery = f'AND `Fields` LIKE \'%{subj}%\'\n'
        conditionQuery = conditionQuery + tempQuery

    query = basicQuery + conditionQuery
    query = query[:-1] + ';'
    
    result = []
    cursor.execute(query)
    for row in cursor:
        result.append({
            "doi":row[0],
            "citations":row[1]
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
