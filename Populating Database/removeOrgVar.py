from pybliometrics.scopus import AffiliationRetrieval
import mysql.connector as connector
from fuzzywuzzy import fuzz
from getpass import getpass


def most_recent(date1, date2):

    return max(date1, date2, key=lambda x: x[::-1])


password = getpass('Enter password: ')

mysqlID = []
mysqlTypes = []
mysqlNames = []
mysqlScopusID = []
mysqlAddresses = []

removedID = []
removedNames = []
remainingNames = []

con = connector.connect(host='localhost',
                        port='3306',
                        user='root',
                        password=password,
                        database='scopus',
                        auth_plugin='mysql_native_password')

cursor = con.cursor()

query = 'SELECT Name FROM organizations;'
cursor.execute(query)
for row in cursor:
    mysqlNames.append(row[0])

query = 'SELECT ID FROM organizations;'
cursor.execute(query)
for row in cursor:
    mysqlID.append(row[0])

query = 'SELECT Scopus_ID FROM organizations;'
cursor.execute(query)
for row in cursor:
    mysqlScopusID.append(row[0])

for i in range(len(mysqlNames)-1):
    for j in range(i+1, len(mysqlNames)):
        if (fuzz.ratio(mysqlNames[i], mysqlNames[j]) > 90) | \
                ((mysqlNames[i] in mysqlNames[j]) | (mysqlNames[j] in mysqlNames[i])):
            date1 = AffiliationRetrieval(int(mysqlScopusID[i])).date_created
            date2 = AffiliationRetrieval(int(mysqlScopusID[j])).date_created
            if most_recent(date1, date2) == date1:
                if mysqlNames[i] not in removedNames:
                    removedID.append(mysqlID[j])
                    removedNames.append(mysqlNames[j])
                    remainingNames.append(mysqlNames[i])
            else:
                if mysqlNames[j] not in removedNames:
                    removedID.append(mysqlID[i])
                    removedNames.append(mysqlNames[i])
                    remainingNames.append(mysqlNames[j])


for i in range(len(removedNames)):
    print(
        f'Remained variant: {remainingNames[i]}| Rejected variant: {removedNames[i]}')

for id in removedID:
    query = 'DELETE FROM authors_organizations WHERE Organization_ID = \'' + \
        str(id) + '\';'
    cursor.execute(query)

    query = 'DELETE FROM publications_organizations WHERE Organization_ID = \'' + \
        str(id) + '\';'
    cursor.execute(query)

    query = 'DELETE FROM organizations WHERE ID = \'' + str(id) + '\';'
    cursor.execute(query)

con.commit()
cursor.close()
con.close()
