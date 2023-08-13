from fuzzywuzzy import fuzz

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
            if ((ids[i] not in variants1Ids) & (ids[i] not in variants2Ids) & ((fuzz.ratio(lastNames[i], lastNames[j]) > 90) 
                & (fuzz.ratio(firstNames[i], firstNames[j]) > 90)) & (((orcidIds[i] is not None) & (orcidIds[j] is not None) 
                & (orcidIds[i] == orcidIds[j])) | (fuzz.ratio(subjectedAreas[i], subjectedAreas[j]) > 90) & (fuzz.ratio(affiliationHistory[i], affiliationHistory[j]) > 90))):

                if (citationsCount[i] > citationsCount[j]):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])

                else:
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
                      
            else:
                break

    # Inserting duplicates in the SQL database
    for i in range(len(variants1Ids)):
        try:
            query = f"INSERT INTO scopus_authors_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
            cursor.execute(query)
            connection.commit()
        except:
            pass