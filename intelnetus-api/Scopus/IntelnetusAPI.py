from ConnectToMySQL.Connector import connect
from flask import Flask, request, jsonify
from flask_cors import CORS
from MetadataManipulation.Extractor import extractMetadata
from InputData.Items import getFullNameFields
from DuplicatesDetection.PublicationsDuplicates import detectPublicationsDuplicates
from DuplicatesDetection.AuthorsDuplicates import detectAuthorsDuplicates
from DuplicatesDetection.OrganizationsDuplicates import detectOrganizationsDuplicates

app = Flask(__name__)
CORS(app)

connection, cursor = connect()

@app.route('/search', methods=['GET'])
def search():

    try:
        keywords = request.args.getlist("keywords")[0].split(',')
        booleans = request.args.getlist("booleans")[0].split(',')
        fields = request.args.getlist("fields")[0].split(',')
        year1 = request.args.get("year1")
        year2 = request.args.get("year2")
        scopusApiKey = request.args.get("scopusApiKey")

        for year in range(int(year1), int(year2)+1):
            extractMetadata(keywords, year, fields, booleans, scopusApiKey, connection, cursor)
        
        #detecting and storing duplicates
        detectPublicationsDuplicates(connection, cursor)
        detectAuthorsDuplicates(connection, cursor)
        detectOrganizationsDuplicates(connection, cursor)

        fullNameFields = getFullNameFields(fields)

        basicQuery = f'SELECT scopus_publications.ID, scopus_publications.DOI, scopus_publications.Title, scopus_publications.Year, scopus_publications.Citations_Count, \n' + \
            'scopus_publications.Keywords, scopus_publications.Fields, scopus_authors.ID, scopus_authors.First_Name, scopus_authors.Last_Name, \n' + \
            'scopus_authors.Fields_Of_Study, scopus_authors.Citations_Count, scopus_authors.hIndex, scopus_organizations.ID, scopus_organizations.Name, \n' + \
            'scopus_organizations.Type_1, scopus_organizations.Type_2, scopus_organizations.City, scopus_organizations.Country \n' + \
            'FROM ((((scopus_publications_authors \n' + \
            'INNER JOIN scopus_publications ON scopus_publications_authors.Publication_ID = scopus_publications.ID) \n' + \
            'INNER JOIN scopus_authors ON scopus_publications_authors.Author_ID = scopus_authors.ID) \n' + \
            'INNER JOIN scopus_authors_organizations ON scopus_authors.ID = scopus_authors_organizations.Author_ID) \n' + \
            'INNER JOIN scopus_organizations ON scopus_authors_organizations.Organization_ID = scopus_organizations.ID)\n'

        conditionQuery = 'WHERE\n (\n'
        for i in range(len(keywords)):
            if (i == 0):
                tempQuery = f'scopus_publications.Keywords LIKE \'%{keywords[i].lower()}%\'\n \
                            OR scopus_publications.Title LIKE \'%{keywords[i].lower()}%\'\n \
                            OR scopus_publications.Abstract LIKE \'%{keywords[i].lower()}%\'\n'
                conditionQuery = conditionQuery + tempQuery
            else:
                tempQuery = f'{booleans[i-1]} `Keywords` LIKE \'%{keywords[i].lower()}%\'\n \
                            OR scopus_publications.Title LIKE \'%{keywords[i].lower()}%\'\n \
                            OR scopus_publications.Abstract LIKE \'%{keywords[i].lower()}%\'\n'
                conditionQuery = conditionQuery + tempQuery
        conditionQuery = conditionQuery + ') \n AND \n'

        conditionQuery = conditionQuery + f'scopus_publications.Year >= {year1}\n'
        conditionQuery = conditionQuery + f'AND scopus_publications.Year <= {year2}\n AND \n (\n'
        for i in range(len(fullNameFields)):
            if (i == 0):
                tempQuery = f'scopus_publications.Fields LIKE \'%{fullNameFields[i]}%\'\n'
                conditionQuery = conditionQuery + tempQuery
            else: 
                tempQuery = f'OR scopus_publications.Fields LIKE \'%{fullNameFields[i]}%\'\n'
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
            organizationsIds.append(row[13])
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
                "authorhIndex":row[12],
                "organizationId":row[13],
                "organizationName":row[14],
                "organizationType1":row[15],
                "organizationType2":row[16],
                "organizationCity":row[17],
                "organizationCountry":row[18]
            })

        # checking got publications duplicates
        publicationsVariants = {
            "originals":[],
            "duplicates":[]
        }
        query = "SELECT * FROM scopus_publications_variants;"
        cursor.execute(query)
        fetchedData = cursor.fetchall()
        for pubVar in fetchedData:
            originalId = pubVar[0]
            duplicateId = pubVar[1]

            if ((originalId in publicationsIds) & (duplicateId in publicationsIds)):
                subQuery = f"SELECT scopus_publications.Id, scopus_publications.Title, scopus_publications.Citations_Count FROM scopus_publications \
                WHERE ID = '{originalId}';"
                cursor.execute(subQuery)
                variantData = cursor.fetchall()[0]
                publicationsVariants["originals"].append({
                    "id":variantData[0],
                    "title":variantData[1],
                    "citationsCount":variantData[2]
                })

                subQuery = f"SELECT scopus_publications.Id, scopus_publications.Title, scopus_publications.Citations_Count FROM scopus_publications \
                WHERE ID = '{duplicateId}';"
                cursor.execute(subQuery)
                variantData = cursor.fetchall()[0]
                publicationsVariants["duplicates"].append({
                    "id":variantData[0],
                    "title":variantData[1],
                    "citationsCount":variantData[2]
                })

        # checking for authors duplicates
        authorsVariants = {
            "originals":[],
            "duplicates":[]
        }
        query = "SELECT * FROM scopus_authors_variants;"
        cursor.execute(query)
        fetchedData = cursor.fetchall()
        for authVar in fetchedData:
            originalId = authVar[0]
            duplicateId = authVar[1]

            if ((originalId in authorsIds) & (duplicateId in authorsIds)):
                subQuery = f"SELECT scopus_authors.Id, scopus_authors.First_Name, scopus_authors.Last_Name, scopus_authors.hIndex, scopus_authors.Citations_Count FROM scopus_authors \
                WHERE ID = '{originalId}';"
                cursor.execute(subQuery)
                variantData = cursor.fetchall()[0]
                authorsVariants["originals"].append({
                    "id":variantData[0],
                    "firstName":variantData[1],
                    "lastName":variantData[2],
                    "hIndex":variantData[3],
                    "citationsCount":variantData[4]
                })

                subQuery = f"SELECT scopus_authors.Id, scopus_authors.First_Name, scopus_authors.Last_Name, scopus_authors.hIndex, scopus_authors.Citations_Count FROM scopus_authors \
                WHERE ID = '{duplicateId}';"
                cursor.execute(subQuery)
                variantData = cursor.fetchall()[0]
                authorsVariants["duplicates"].append({
                    "id":variantData[0],
                    "firstName":variantData[1],
                    "lastName":variantData[2],
                    "hIndex":variantData[3],
                    "citationsCount":variantData[4]
                })

        # checking for organizations duplicates
        organizationsVariants = {
            "originals":[],
            "duplicates":[]
        }
        query = "SELECT * FROM scopus_organizations_variants;"
        cursor.execute(query)
        fetchedData = cursor.fetchall()
        for orgVar in fetchedData:
            originalId = orgVar[0]
            duplicateId = orgVar[1]

            if ((originalId in organizationsIds) & (duplicateId in organizationsIds)):
                subQuery = f"SELECT scopus_organizations.Id, scopus_organizations.Name FROM scopus_organizations \
                WHERE ID = '{originalId}';"
                cursor.execute(subQuery)
                variantData = cursor.fetchall()[0]
                organizationsVariants["originals"].append({
                    "id":variantData[0],
                    "name":variantData[1]
                })

                subQuery = f"SELECT scopus_organizations.Id, scopus_organizations.Name FROM scopus_organizations \
                WHERE ID = '{duplicateId}';"
                cursor.execute(subQuery)
                variantData = cursor.fetchall()[0]
                organizationsVariants["duplicates"].append({
                    "id":variantData[0],
                    "name":variantData[1]
                })

        variants = {
            "publicationsVariants":publicationsVariants,
            "authorsVariants":authorsVariants,
            "organizationsVariants":organizationsVariants
        }

        if (len(data) > 0):
            result = {
                "successful":"true",
                "hasResult":"true",
                "data":data,
                "variants":variants
            }
        else:
            result = {
                "successful":"true",
                "hasResult":"false",
                "data":data,
                "variants":variants
            }
    
    except:
        result = {
            "successful":"false",
            "hasResult":"false",
            "data":[],
            "variants":[]
        }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
