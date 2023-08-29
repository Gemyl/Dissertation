from fuzzywuzzy import fuzz

def detectAuthorsDuplicates(connection, cursor):

    ids = []
    orcidIds = []
    lastNames = []
    firstNames = []
    subjectedAreas = []
    affiliationHistory = []
    citationsCount = []

    primaryVariants = []
    secondaryVariants = []

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

            if (((fuzz.ratio(lastNames[i], lastNames[j]) > 90) & (fuzz.ratio(firstNames[i], firstNames[j]) > 90)) 
                & (((orcidIds[i] is not None) & (orcidIds[j] is not None) & (orcidIds[i] == orcidIds[j])) 
                | (fuzz.ratio(subjectedAreas[i], subjectedAreas[j]) > 90) & (fuzz.ratio(affiliationHistory[i], affiliationHistory[j]) > 90))):

                if ((citationsCount[i] > citationsCount[j]) ):
                    if((ids[i] in secondaryVariants) & (ids[j] not in secondaryVariants)):
                        index = secondaryVariants.index(ids[i])
                        primaryVariants.append(primaryVariants[index])
                        secondaryVariants.append(ids[j])

                    elif(ids[j] not in secondaryVariants):
                        primaryVariants.append(ids[i])
                        secondaryVariants.append(ids[j])

                else:
                    if((ids[j] in secondaryVariants) & (ids[i] not in secondaryVariants)):
                        index = secondaryVariants.index(ids[j])
                        primaryVariants.append(primaryVariants[index])
                        secondaryVariants.append(ids[i])

                    elif(ids[i] not in secondaryVariants):
                        primaryVariants.append(ids[j])
                        secondaryVariants.append(ids[i])
                      
            else:
                break

    for i in range(len(primaryVariants)):
        try:
            query = f"INSERT INTO scopus_authors_variants VALUES ('{primaryVariants[i]}', '{secondaryVariants[i]}');"
            cursor.execute(query)
            connection.commit()
        except:
            pass