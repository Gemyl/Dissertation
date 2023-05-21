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


@app.route('/search', methods=['GET'])
def search():

    keywords = request.args.getlist('keywords')[0].split(',')
    booleans = request.args.getlist('booleans')[0].split(',')
    fields = request.args.getlist('fields')[0].split(',')
    year1 = request.args.get("year1")
    year2 = request.args.get("year2")

    basicQuery = f'SELECT scopus_publications.ID, scopus_publications.DOI, scopus_publications.Title, scopus_publications.Year, scopus_publications.Citations_Count, \n' + \
        'scopus_publications.Keywords, scopus_publications.Fields, scopus_authors.ID, scopus_authors.First_Name, scopus_authors.Last_Name, \n' + \
        'scopus_authors.Fields_Of_Study, scopus_authors.Citations_Count, scopus_organizations.ID, scopus_organizations.Name, \n' + \
        'scopus_organizations.Type_1, scopus_organizations.Type_2, scopus_organizations.City, scopus_organizations.Country \n' + \
        'FROM ((((scopus_publications_authors \n' + \
        'INNER JOIN scopus_publications ON scopus_publications_authors.Publication_ID = scopus_publications.ID) \n' + \
        'INNER JOIN scopus_authors ON scopus_publications_authors.Author_ID = scopus_authors.ID) \n' + \
        'INNER JOIN scopus_authors_organizations ON scopus_authors.ID = scopus_authors_organizations.Author_ID) \n' + \
        'INNER JOIN scopus_organizations ON scopus_authors_organizations.Organization_ID = scopus_organizations.ID)\n'

    conditionQuery = 'WHERE\n (\n'
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
    
    conditionQuery = conditionQuery + ');'
    query = basicQuery + conditionQuery

    data = []
    publicationsIds = []
    authorsIds = []
    organizationsIds = []
    cursor.execute(query)
    metadata = cursor.fetchall()
    for row in metadata:
        publicationsIds.append(row[0])
        authorsIds.append(row[7])
        organizationsIds.append(row[12])
        data.append({
            "publicationId":row[0],
            "publicationDoi":row[1],
            "publicationTitle":row[2],
            "publicationYear":row[3],
            "publicationCitationsCount":row[4],
            "publicationKeywords":row[5],
            "publicationFields":row[6],
            "authorId":row[7],
            "authorFirstName":row[8],
            "authorLastName":row[9],
            "authorFieldsOfStudy":row[10],
            "authorCitationsCount":row[11],
            "organizationId":row[12],
            "organizationName":row[13],
            "organizationType1":row[14],
            "organizationType2":row[15],
            "organizationCity":row[16],
            "organizationCountry":row[17]
        })

    # checking got publications duplicates
    publicationsVariants = {
        "variants1":[],
        "variants2":[]
    }
    query = "SELECT * FROM scopus_publications_variants;"
    cursor.execute(query)
    fetchedData = cursor.fetchall()
    for pubVar in fetchedData:
        var1Id = pubVar[0]
        var2Id = pubVar[1]

        if ((var1Id in publicationsIds) & (var2Id in publicationsIds)):
            subQuery = f"SELECT scopus_publications.Id, scopus_publications.Title, scopus_publications.Citations_Count FROM scopus_publications \
            WHERE ID = '{var1Id}';"
            cursor.execute(subQuery)
            variantData = cursor.fetchall()[0]
            publicationsVariants["variants1"].append({
                "id":variantData[0],
                "title":variantData[1],
                "citationsCount":variantData[2]
            })

            subQuery = f"SELECT scopus_publications.Id, scopus_publications.Title, scopus_publications.Citations_Count FROM scopus_publications \
            WHERE ID = '{var2Id}';"
            cursor.execute(subQuery)
            variantData = cursor.fetchall()[0]
            publicationsVariants["variants2"].append({
                "id":variantData[0],
                "title":variantData[1],
                "citationsCount":variantData[2]
            })

    # checking for authors duplicates
    authorsVariants = {
        "variants1":[],
        "variants2":[]
    }
    query = "SELECT * FROM scopus_authors_variants;"
    cursor.execute(query)
    fetchedData = cursor.fetchall()
    for authVar in fetchedData:
        var1Id = authVar[0]
        var2Id = authVar[1]

        if ((var1Id in authorsIds) & (var2Id in authorsIds)):
            subQuery = f"SELECT scopus_authors.Id, scopus_authors.First_Name, scopus_authors.Last_Name, scopus_authors.hIndex, scopus_authors.Citations_Count FROM scopus_authors \
            WHERE ID = '{var1Id}';"
            cursor.execute(subQuery)
            variantData = cursor.fetchall()[0]
            authorsVariants["variants1"].append({
                "id":variantData[0],
                "firstName":variantData[1],
                "lastName":variantData[2],
                "hIndex":variantData[3],
                "citationsCount":variantData[4]
            })

            subQuery = f"SELECT scopus_authors.Id, scopus_authors.First_Name, scopus_authors.Last_Name, scopus_authors.hIndex, scopus_authors.Citations_Count FROM scopus_authors \
            WHERE ID = '{var2Id}';"
            cursor.execute(subQuery)
            variantData = cursor.fetchall()[0]
            authorsVariants["variants2"].append({
                "id":variantData[0],
                "firstName":variantData[1],
                "lastName":variantData[2],
                "hIndex":variantData[3],
                "citationsCount":variantData[4]
            })

    # checking for organizations duplicates
    organizationsVariants = {
        "variants1":[],
        "variants2":[]
    }
    query = "SELECT * FROM scopus_organizations_variants;"
    cursor.execute(query)
    fetchedData = cursor.fetchall()
    for orgVar in fetchedData:
        var1Id = orgVar[0]
        var2Id = orgVar[1]

        if ((var1Id in organizationsIds) & (var2Id in organizationsIds)):
            subQuery = f"SELECT scopus_organizations.Id, scopus_organizations.Name FROM scopus_organizations \
            WHERE ID = '{var1Id}';"
            cursor.execute(subQuery)
            variantData = cursor.fetchall()[0]
            organizationsVariants["variants1"].append({
                "id":variantData[0],
                "name":variantData[1]
            })

            subQuery = f"SELECT scopus_organizations.Id, scopus_organizations.Name FROM scopus_organizations \
            WHERE ID = '{var2Id}';"
            cursor.execute(subQuery)
            variantData = cursor.fetchall()[0]
            organizationsVariants["variants2"].append({
                "id":variantData[0],
                "name":variantData[1]
            })

    variants = {
        "publicationVariants":publicationsVariants,
        "authorVariants":authorsVariants,
        "organizationVariants":organizationsVariants
    }

    result = {
        "data":data,
        "variants":variants
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
