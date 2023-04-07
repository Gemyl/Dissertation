from pybliometrics.scopus import AffiliationRetrieval
import mysql.connector as connector
from fuzzywuzzy import fuzz
from getpass import getpass


def most_recent(date1, date2):

    return max(date1, date2, key=lambda x: x[::-1])


password = 'gemyl'

id = []
lastNames = []
firstNames = []
subjectedAreas = []
citationsCount = []

removedID = []
removedNames = []
remainingNames = []

con = connector.connect(host='localhost',
                        port='3306',
                        user='root',
                        password=password,
                        database='george',
                        auth_plugin='mysql_native_password')

cursor = con.cursor()

query = 'SELECT ID FROM authors ORDER BY ID;'
cursor.execute(query)
for row in cursor:
    id.append(row[0])

query = 'SELECT Subjected_Areas FROM authors ORDER BY ID;'
cursor.execute(query)
for row in cursor:
    subjectedAreas.append(row[0])

query = 'SELECT First_Name FROM authors ORDER BY ID;'
cursor.execute(query)
for row in cursor:
    firstNames.append(row[0])

query = 'SELECT Last_Name FROM authors ORDER BY ID;'
cursor.execute(query)
for row in cursor:
    lastNames.append(row[0])

query = 'SELECT Item_Citations_Count FROM authors ORDER BY ID;'
cursor.execute(query)
for row in cursor:
    citationsCount.append(row[0])


for i in range(len(subjectedAreas)-1):

    iFullName = firstNames[i] + ' ' + lastNames[i]

    for j in range(i+1, len(subjectedAreas)):

        jFullName = firstNames[j] + ' ' + lastNames[j]

        similarity = fuzz.ratio(subjectedAreas[i], subjectedAreas[j])
        if (fuzz.ratio(subjectedAreas[i], subjectedAreas[j]) > 90) & (iFullName == jFullName):

            iCitations = citationsCount[i]
            jCitations = citationsCount[j]

            try:
                if iCitations > jCitations:
                    if iFullName not in removedNames:
                        removedID.append(id[j])
                        removedNames.append(jFullName)
                        remainingNames.append(iFullName)
                else:
                    if jFullName not in removedNames:
                        removedID.append(id[i])
                        removedNames.append(iFullName)
                        remainingNames.append(jFullName)
            except:
                continue


for i in range(len(removedNames)):
    print(
        f'Remained variant: {remainingNames[i]}| Rejected variant: {removedNames[i]}')

for id in removedID:
    query = 'DELETE FROM authors_organizations WHERE Author_ID = ' + \
        str(id) + ';'
    cursor.execute(query)

    query = 'DELETE FROM publications_authors WHERE Author_ID = ' + \
        str(id) + ';'
    cursor.execute(query)

    query = 'DELETE FROM authors WHERE ID = ' + str(id) + ';'
    cursor.execute(query)

con.commit()
cursor.close()
con.close()
