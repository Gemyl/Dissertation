from pybliometrics.scopus import AffiliationRetrieval
import mysql.connector as connector
from fuzzywuzzy import fuzz
from getpass import getpass

# Colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"
BLUE = "\033[1;34m"

# Reset color to default
RESET = "\033[0m"

def detectAuthorsDuplicates(connection, cursor):
    # Lists for storing SQL data
    ids = []
    orcidIds = []
    lastNames = []
    firstNames = []
    subjectedAreas = []
    affiliationHistory = []
    citationsCount = []

    # Lists for concetrating removed and remaining variants
    variants1Ids = []
    variants2Ids = []
    removedNames = []
    remainingNames = []

    # Retrieving data from database
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

    # Duplicates detection algorithm
    for i in range(len(ids) - 1):
        for j in range(i + 1, len(ids)):
            if (((fuzz.ratio(lastNames[i], lastNames[j]) > 90) & (fuzz.ratio(firstNames[i], firstNames[j]) > 90)) & 
                ((orcidIds[i] is not None) & (orcidIds[j] is not None) & (orcidIds[i] == orcidIds[j])) |
                (fuzz.ratio(subjectedAreas[i], subjectedAreas[j]) > 90) & (fuzz.ratio(affiliationHistory[i], affiliationHistory[j]) > 90)):

                if ((citationsCount[i] > citationsCount[j]) & (ids[i] not in variants2Ids)):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])
                    removedNames.append(f"{firstNames[j]} {lastNames[j]}")
                    remainingNames.append(f"{firstNames[i]} {lastNames[i]}")

                elif (ids[j] not in variants2Ids):
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
                    removedNames.append(f"{firstNames[i]} {lastNames[i]}")
                    remainingNames.append(f"{firstNames[j]} {lastNames[j]}")
            else:
                break

    if (len(removedNames) == 0):
        print(f"{BLUE}No duplicates detected.")
    else:
        for i in range(len(removedNames)):
            print(f'------------------\n'
                f'{GREEN}Remained variant: {remainingNames[i]}{RESET}\n'
                f'{RED}Rejected variant: {removedNames[i]}{RESET}\n'
                f'------------------')
            try:
                query = f"INSERT INTO scopus_authors_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
                cursor.execute(query)
                connection.commit()
            except:
                pass