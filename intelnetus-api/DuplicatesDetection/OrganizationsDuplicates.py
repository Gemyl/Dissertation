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

def getMostRecentProfile(first_date, seconnectiond_date):
    """Return the most recent date between two dates."""
    return max(first_date, seconnectiond_date, key=lambda x: x[::-1])


def detectOrganizationsDuplicates(connection, cursor):
    # Initialize lists to store organization data
    ids = []
    names = []
    scopusIds = []
    addresses = []

    # Initialize lists to store rejected organization data
    variants1Ids = []
    variants2Ids = []
    removedNames = []
    remainingNames = []
    # Retrieve organization data from database

    query = 'SELECT Name FROM scopus_organizations ORDER BY Name;'
    cursor.execute(query)
    for row in cursor:
        names.append(row[0])

    query = 'SELECT ID FROM scopus_organizations ORDER BY Name;'
    cursor.execute(query)
    for row in cursor:
        ids.append(row[0])

    query = 'SELECT Scopus_ID FROM scopus_organizations ORDER BY Name;'
    cursor.execute(query)
    for row in cursor:
        scopusIds.append(row[0])

    query = 'SELECT Address FROM scopus_organizations ORDER BY Name;'
    cursor.execute(query)
    for row in cursor:
        addresses.append(row[0])

    # Compare each pair of organization names and determine which variant to keep
    for i in range(len(names)-1):
        for j in range(i+1, len(names)):

            # Check if names are similar and addresses are the same
            if ((ids[i] not in variants2Ids) & ((fuzz.ratio(names[i], names[j]) > 85) | (names[i] in names[j]) | (names[j] in names[i])) &
                (addresses[i] == addresses[j])):
                first_date = AffiliationRetrieval(int(scopusIds[i])).date_created
                second_date = AffiliationRetrieval(int(scopusIds[j])).date_created

                # Keep the organization with the most recent profile
                if (getMostRecentProfile(first_date, second_date) == first_date):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])
                    removedNames.append(names[j])
                    remainingNames.append(names[i])
                
                else:
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
                    removedNames.append(names[i])
                    remainingNames.append(names[j])
                    
            else:
                break

    # Print out the rejected and remaining organization variants
    if(len(removedNames) == 0):
        print(f"{BLUE}No duplicates detected for fetched organizations records.{RESET}")
    else:
        for i in range(len(removedNames)):
            print(f'----------------\n'
                f'{GREEN}Remained variant: {remainingNames[i]}{RESET}\n'
                f'{RED}Rejected variant: {removedNames[i]}{RESET}\n'
                f'----------------')
            
            try:
                query = f"INSERT INTO scopus_organizations_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
                cursor.execute(query)
                connection.commit()
            except:
                pass
