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


# Get password from user input
password = getpass('Enter password: ')

# Initialize lists to store organization data
ids = []
names = []
scopusIds = []
cities = []

# Initialize lists to store rejected organization data
removedIds = []
removedNames = []
remainingNames = []

# connectionnect to MySQL database
connection = connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password=password,
    database='scopus',
    auth_plugin='mysql_native_password'
)

# Create cursor object to execute queries
cursor = connection.cursor()

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

query = 'SELECT City FROM scopus_organizations ORDER BY Name;'
cursor.execute(query)
for row in cursor:
    cities.append(row[0])

# Compare each pair of organization names and determine which variant to keep
for i in range(len(names)-1):
    for j in range(i+1, len(names)):

        # Check if names are similar and cities are the same
        if (((fuzz.ratio(names[i], names[j]) > 85) | (names[i] in names[j]) | (names[j] in names[i])) &
            (cities[i] == cities[j])):
            first_date = AffiliationRetrieval(int(scopusIds[i])).date_created
            seconnectiond_date = AffiliationRetrieval(int(scopusIds[j])).date_created

            # Keep the organization with the most recent profile
            if ((getMostRecentProfile(first_date, seconnectiond_date) == first_date) & (ids[i] not in removedIds)):
                removedIds.append(ids[j])
                removedNames.append(names[j])
                remainingNames.append(names[i])
                
            elif (names[j] not in removedNames):
                    removedIds.append(ids[i])
                    removedNames.append(names[i])
                    remainingNames.append(names[j])
        else:
            break

# Print out the rejected and remaining organization variants
if(len(removedNames) == 0):
    print(f"{BLUE}No duplicates detected.")
else:
    for i in range(len(removedNames)):
        print(f'----------------\n'
            f'{GREEN}Remained variant: {remainingNames[i]}{RESET}\n'
            f'{RED}Rejected variant: {removedNames[i]}{RESET}\n'
            f'----------------')

# Close the cursor and database connectionnection
cursor.close()
connection.close()