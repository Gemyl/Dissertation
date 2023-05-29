from pybliometrics.scopus import AffiliationRetrieval
from fuzzywuzzy import fuzz

# Colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

def getMostRecentProfile(first_date, seconnectiond_date):
    """Return the most recent date between two dates."""
    return max(first_date, seconnectiond_date, key=lambda x: x[::-1])

def detectPublicationsDuplicates(connection, cursor):
    # lists for storing data fetched from database
    ids = []
    dois = []
    titles = []
    abstracts = []
    keywords = []
    fields = []
    citationsCount = []

    # lists concetrating remained and removed variants
    variants1Ids = []
    variants2Ids = []
    removedTitles = []
    remainingTitles =[]

    # Retrieving data from database
    query = "SELECT ID FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        ids.append(row[0])

    query = "SELECT DOI FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        dois.append(row[0])

    query = "SELECT Title FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        titles.append(row[0])

    query = "SELECT Abstract FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        abstracts.append(row[0])

    query = "SELECT Keywords FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        keywords.append(row[0])

    query = "SELECT Fields FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        fields.append(row[0])

    query = "SELECT Citations_Count FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        citationsCount.append(row[0])

    # Duplicates detection algorithm
    for i in range(len(ids)-1):
        for j in range(i+1, len(ids)):

            if((fuzz.ratio(titles[i], titles[j]) > 85) & (fuzz.ratio(abstracts[i], abstracts[j]) > 85) & 
            (fuzz.ratio(keywords[i], keywords[j]) > 85) & (fuzz.ratio(fields[i], fields[j]) > 85)):
                firstPublicationCitations = citationsCount[i]
                seconnectiondPublicationCitations = citationsCount[j]

                if ((firstPublicationCitations > seconnectiondPublicationCitations) & (ids[i] not in variants2Ids)):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])
                    removedTitles.append(titles[j])
                    remainingTitles.append(titles[i])

                elif (ids[j] not in variants2Ids):
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
                    removedTitles.append(titles[i])
                    remainingTitles.append(titles[j])
            else:
                break

    # Printing results
    if len(removedTitles) == 0:
        print(f"{BLUE}No duplicates detected.")
    else:
        for i in range(len(removedTitles)):
            print(f'------------------\n'
                f'{GREEN}Remained variant: {remainingTitles[i]}{RESET}.\n'
                f'{RED}Rejected variant: {removedTitles[i]}{RESET}.\n'
                f'------------------')
            
            try:
                query = f"INSERT INTO scopus_publications_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
                cursor.execute(query)
                connection.commit()
            except:
                pass

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

    # Printing results
    print(len(removedNames))
    print(len(variants1Ids))
    print(len(variants2Ids))
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

def detectOrganizationsDuplicates(connection, cursor):
    # Initialize lists to store organization data
    ids = []
    names = []
    scopusIds = []
    cities = []

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
                if ((getMostRecentProfile(first_date, seconnectiond_date) == first_date) & (ids[i] not in variants2Ids)):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])
                    removedNames.append(names[j])
                    remainingNames.append(names[i])
                    
                elif (ids[j] not in variants2Ids):
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
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
            
            try:
                query = f"INSERT INTO scopus_organizations_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
                cursor.execute(query)
                connection.commit()
            except:
                pass