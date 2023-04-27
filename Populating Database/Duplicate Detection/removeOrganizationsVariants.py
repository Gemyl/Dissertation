from pybliometrics.scopus import AffiliationRetrieval
import mysql.connector as connector
from fuzzywuzzy import fuzz
from getpass import getpass

# Colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"

# Reset color to default
RESET = "\033[0m"

def getMostRecentProfile(first_date, second_date):
    """Return the most recent date between two dates."""
    return max(first_date, second_date, key=lambda x: x[::-1])


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

# Connect to MySQL database
con = connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password=password,
    database='scopus',
    auth_plugin='mysql_native_password'
)

# Create cursor object to execute queries
cursor = con.cursor()

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
            second_date = AffiliationRetrieval(int(scopusIds[j])).date_created

            # Keep the organization with the most recent profile
            if getMostRecentProfile(first_date, second_date) == first_date:
                if names[i] not in removedNames:
                    removedIds.append(ids[j])
                    removedNames.append(names[j])
                    remainingNames.append(names[i])
            else:
                if names[j] not in removedNames:
                    removedIds.append(ids[i])
                    removedNames.append(names[i])
                    remainingNames.append(names[j])
        else:
            break

# Print out the rejected and remaining organization variants
for i in range(len(removedNames)):
    print(f'----------------\n{GREEN}Remained variant: {remainingNames[i]}{RESET} \n{RED}Rejected variant: {removedNames[i]}{RESET} \n----------------')

# Uncomment the following code to delete rejected organizations from the database
# for id in removed_id:
#     query = 'DELETE FROM authors_organizations WHERE Organization_ID = \'' + \
#         str(id) + '\';'
#     cursor.execute(query)

#     query = 'DELETE FROM publications_organizations WHERE Organization_ID = \'' + \
#         str(id) + '\';'
#     cursor.execute(query)

#     query = 'DELETE FROM organizations WHERE ID = \'' + str(id) + '\';'
#     cursor.execute(query)

# Commit changes to the database
con.commit()

# Close the cursor and database connection
cursor.close()
con.close()
