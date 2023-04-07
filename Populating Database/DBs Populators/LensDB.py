import mysql.connector as connector
from getpass import getpass
from tqdm import tqdm
import requests
import json
import uuid


# getting length of columns
def getColumnLength(column, table, cursor):
    try:
        query = f"SELECT LENGTH({column}) FROM {table};"
        cursor.execute(query)
        result_set = cursor.fetchall()
        return result_set[0][0]
    except:
        return 100


# establishing connection with MySQL DB
password = getpass()
connection = connector.connect(host='localhost',
                               port='3306',
                               user='root',
                               password=password,
                               database='lens',
                               auth_plugin='mysql_native_password')
cursor = connection.cursor()

# non-standard length columns initial number of characters
titleLength = getColumnLength('Title', 'lens_publications', cursor)
abstractLength = getColumnLength('Abstract', 'lens_publications', cursor)
keywordsLength = getColumnLength('Keywords', 'lens_publications', cursor)
fieldsLength = getColumnLength('Fields', 'lens_publications', cursor)
syntheticIdLength = getColumnLength('Synthetic_ID', 'lens_authors', cursor)
firstNameLength = getColumnLength('First_Name', 'lens_authors', cursor)
lastNameLength = getColumnLength('Last_Name', 'lens_authors', cursor)
initialsLength = getColumnLength('Initials', 'lens_authors', cursor)
authorAffilLength = getColumnLength('Affiliations', 'lens_authors', cursor)
affilNameLength = getColumnLength('Name', 'lens_organizations', cursor)

# list of common words in order to be removed from abstracts
commonWords = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about',
               'to', 'from', 'in', 'on', 'up', 'out', 'as', 'into', 'through', 'over', 'after', 'under',
               'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'has', 'had',
               'will', 'be', 'not', 'would', 'should', 'before', 'few', 'many', 'much', 'so', 'furthermore']

# endpoint URL and parameters
endpoint = "https://api.lens.org/scholarly/search"
parameters = {
    "token": "un4zoq8tBzXtzzfscXEnh3dWaGDLcTdCNcQzeaMPpThLwq4fIgvs",
    "size": "1000",
    "query": "pattern recognition",
    "include": "lens_id, year_published, title, abstract, keywords, fields_of_study, \
                scholarly_citations_count, author_count, authors"
}

# getting response
response = requests.get(endpoint, params=parameters)
metadata = json.loads(response.content)
publicationsMetadata = metadata['data']

# for each publication ...
for publication in tqdm(publicationsMetadata):

    # getting these metadata
    pubId = str(uuid.uuid4())
    lensId = publication['lens_id']
    if "year_published" in publication.keys():
        year = str(publication['year_published'])
    else:
        year = "9999"

    if "title" in publication.keys():
        title = publication['title'].replace("\'", "\\\'")
    else:
        title = "-"

    if "abstract" in publication.keys():
        abstract = publication['abstract'].replace("\'", "\\\'")
        abstract = " ".join([word for word in abstract.split(" ")
                             if word.lower() not in commonWords])
    else:
        abstract = "-"

    if "keywords" in publication.keys():
        keywords = ", ".join(publication['keywords']).replace("\'", "\\\'")
    else:
        keywords = "-"

    if "fields_of_study" in publication.keys():
        fields = ", ".join(
            publication['fields_of_study']).replace("\'", "\\\'")
    else:
        fields = "-"

    if "scholarly_citations_count" in publication.keys():
        citationsCount = str(publication['scholarly_citations_count'])
    else:
        citationsCount = "999999"

    if "author_count" in publication.keys():
        authorsCount = str(publication['author_count'])
    else:
        authorsCount = "999999"

    while True:
        # and attempt to insert them in MySQL DB
        try:
            query = f"INSERT INTO lens_publications VALUES('{pubId}','{lensId}',{year},'{title}','{abstract}','{keywords}',\
                '{fields}',{citationsCount}, {authorsCount});"
            cursor.execute(query)
            connection.commit()

            # for each publications author ...
            if "authors" in publication.keys():
                for author in publication['authors']:

                    # getting these data
                    authorId = str(uuid.uuid4())
                    if ("ids" in author.keys()) & (author['ids'] != None):
                        syntheticId = "".join([id['value']
                                              for id in author['ids']])

                    if "first_name" in author.keys():
                        firstName = author['first_name'].replace("\'", "\\\'")
                    else:
                        firstName = "-"

                    if "last_name" in author.keys():
                        lastName = author['last_name'].replace("\'", "\\\'")
                    else:
                        lastName = "-"

                    if "initials" in author.keys():
                        initials = author['initials'].replace("\'", "\\\'")
                    else:
                        initials = "-"

                    if "affiliations" in author.keys():
                        affiliations = ", ".join(
                            [affil['name'] for affil in author['affiliations']]).replace("\'", "\\\'")
                    else:
                        affiliations = "-"

                    while True:
                        try:
                            # and attempt to insert them in MySQL DB
                            query = f"INSERT INTO lens_authors VALUES('{authorId}','{syntheticId}','{firstName}','{lastName}', \
                            '{initials}', '{affiliations}');"
                            cursor.execute(query)
                            connection.commit()

                            # insert row in relation publications - authors table
                            query = f"INSERT INTO lens_publications_authors VALUES('{pubId}','{authorId}');"
                            cursor.execute(query)
                            connection.commit()

                            # getting affiliations metadata
                            if "affiliations" in author.keys():
                                for affil in author['affiliations']:

                                    affilId = str(uuid.uuid4())

                                    if "name" in affil.keys():
                                        affilName = affil['name'].replace(
                                            "\'", "\\\'")
                                    else:
                                        affilName = "-"

                                    if "country" in affil.keys():
                                        affilCountry = affil['country_code']
                                    else:
                                        affilCountry = "-"

                                    while True:
                                        try:
                                            query = f"INSERT INTO lens_organizations VALUES('{affilId}','{affilName}','{affilCountry}');"
                                            cursor.execute(query)
                                            connection.commit()

                                            # authors - organizations matching storation
                                            query = f"INSERT INTO lens_authors_organizations VALUES('{authorId}','{affilId}');"
                                            cursor.execute(query)
                                            connection.commit()

                                            # publications - organizations matching storation
                                            query = f"INSERT INTO lens_publications_organizations VALUES('{pubId}','{affilId}');"
                                            cursor.execute(query)
                                            connection.commit()

                                            break

                                        except Exception as err:
                                            if ("Duplicate entry" not in str(err)) & ("Unread result found" not in str(err)):
                                                print(f"Error: {str(err)}")

                                                if "Data too long" in str(err):
                                                    try:
                                                        affilNameLength += 10
                                                        query = f"ALTER TABLE lens_organizations MODIFY COLUMN Name VARCHAR({affilNameLength});"
                                                        cursor.execute(query)
                                                        connection.commit()
                                                    except:
                                                        pass
                                            else:
                                                break
                            break

                        except Exception as err:
                            print(f"Error: {str(err)}")

                            if "Data too long" in str(err):
                                if "Synthetic_ID" in str(err):
                                    try:
                                        syntheticIdLength += 5
                                        query = f"ALTER TABLE lens_authors MODIFY COLUMN Synthetic_ID VARCHAR({syntheticIdLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                if "First_Name" in str(err):
                                    try:
                                        firstName += 10
                                        query = f"ALTER TABLE lens_authors MODIFY COLUMN First_Name VARCHAR({firstNameLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                if "Last_Name" in str(err):
                                    try:
                                        lastName += 10
                                        query = f"ALTER TABLE lens_authors MODIFY COLUMN Last_Name VARCHAR({lastNameLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                if "Initials" in str(err):
                                    try:
                                        initialsLength += 1
                                        query = f"ALTER TABLE lens_authors MODIFY COLUMN Initials VARCHAR({initialsLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass

                                if "Affiliations" in str(err):
                                    try:
                                        authorAffilLength += 10
                                        query = f"ALTER TABLE lens_authors MODIFY COLUMN Affiliations VARCHAR({authorAffilLength});"
                                        cursor.execute(query)
                                        connection.commit()
                                    except:
                                        pass
                            else:
                                break

            break

        except Exception as err:
            print(f"Error: {str(err)}")

            # if data too long, extend the corresponding column
            if "Data too long" in str(err):
                if "Title" in str(err):
                    try:
                        titleLength += 100
                        query = f"ALTER TABLE lens_publications MODIFY COLUMN Title VARCHAR({titleLength});"
                        cursor.execute(query)
                        connection.commit()
                    except:
                        pass

                elif "Abstract" in str(err):
                    try:
                        abstractLength += 100
                        if abstractLength > 8000:
                            break
                        query = f"ALTER TABLE lens_publications MODIFY COLUMN Abstract VARCHAR({abstractLength});"
                        cursor.execute(query)
                        connection.commit()
                    except:
                        pass

                elif "Keywords" in str(err):
                    try:
                        keywordsLength += 100
                        query = f"ALTER TABLE lens_publications MODIFY COLUMN Keywords VARCHAR({keywordsLength});"
                        cursor.execute(query)
                        connection.commit()
                    except:
                        pass

                elif "Fields" in str(err):
                    try:
                        fieldsLength += 100
                        query = f"ALTER TABLE lens_publications MODIFY COLUMN Fields VARCHAR({fieldsLength});"
                        cursor.execute(query)
                        connection.commit()
                    except:
                        pass
            else:
                break


# closing connection with MySQL DB
cursor.close()
connection.close()
