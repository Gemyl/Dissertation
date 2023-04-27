from pybliometrics.scopus import AffiliationRetrieval
import mysql.connector as connector
from fuzzywuzzy import fuzz
from getpass import getpass

# Colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"

# Reset color to default
RESET = "\033[0m"

ids = []
orcidIds = []
scopusIds = []
lastNames = []
firstNames = []
subjectedAreas = []
affiliationHistory = []
citationsCount = []

removedIds = []
removedNames = []
remainingNames = []

password = getpass("Enter password: ")
con = connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password=password,
    database='scopus',
    auth_plugin='mysql_native_password'
)

cursor = con.cursor()

query = 'SELECT ID FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    ids.append(row[0])

query = 'SELECT ORCID_ID FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    orcidIds.append(row[0])

query = 'SELECT First_Name FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    firstNames.append(row[0])

query = 'SELECT Last_Name FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    lastNames.append(row[0])

query = 'SELECT Fields_Of_Study FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    subjectedAreas.append(row[0])

query = 'SELECT Affiliations FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    affiliationHistory.append(row[0])

query = 'SELECT Citations_Count FROM scopus_authors ORDER BY Last_Name;'
cursor.execute(query)
for row in cursor:
    citationsCount.append(row[0])

for i in range(len(ids) - 1):
    for j in range(i + 1, len(ids)):
        if ((fuzz.ratio(lastNames[i], lastNames[j]) > 85) &
            (fuzz.ratio(firstNames[i], firstNames[j]) > 85)):
            if (((orcidIds[i] is not None) & (orcidIds[j] is not None) &
                (orcidIds[i] == orcidIds[j])) |
                (fuzz.ratio(subjectedAreas[i], subjectedAreas[j]) > 85) &
                (fuzz.ratio(affiliationHistory[i], affiliationHistory[j]))):
                if (citationsCount[i] > citationsCount[j]):
                    removedIds.append(ids[j])
                    removedNames.append(
                        f"{firstNames[j]} {lastNames[j]}"
                    )
                    remainingNames.append(
                        f"{firstNames[i]} {lastNames[i]}"
                    )
                else:
                    removedIds.append(ids[i])
                    removedNames.append(
                        f"{firstNames[i]} {lastNames[i]}"
                    )
                    remainingNames.append(
                        f"{firstNames[j]} {lastNames[j]}"
                    )
        else:
            break

for i in range(len(removedNames)):
    print(f'------------------\n'
          f'{GREEN}Remained variant: {remainingNames[i]}{RESET}\n'
          f'{RED}Rejected variant: {removedNames[i]}{RESET}\n'
          f'------------------')


# for id in removedIds:
#     query = 'DELETE FROM authors_organizations WHERE Author_ID = ' + \
#         str(id) + ';'
#     cursor.execute(query)

#     query = 'DELETE FROM publications_authors WHERE Author_ID = ' + \
#         str(id) + ';'
#     cursor.execute(query)

#     query = 'DELETE FROM authors WHERE ID = ' + str(id) + ';'
#     cursor.execute(query)

# con.commit()
cursor.close()
con.close()
