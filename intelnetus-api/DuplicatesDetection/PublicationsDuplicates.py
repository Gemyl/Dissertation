from fuzzywuzzy import fuzz

def detectPublicationsDuplicates(connection, cursor):

    ids = []
    dois = []
    titles = []
    abstracts = []
    keywords = []
    fields = []
    citationsCount = []

    primaryVariants = []
    secondaryVariants = []

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

    for i in range(len(ids)-1):
        for j in range(i+1, len(ids)):

            if((fuzz.ratio(titles[i], titles[j]) > 85) & (fuzz.ratio(abstracts[i], abstracts[j]) > 85) 
            & (fuzz.ratio(keywords[i], keywords[j]) > 85) & (fuzz.ratio(fields[i], fields[j]) > 85)):

                if (citationsCount[i] > citationsCount[j]):
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
            query = f"INSERT INTO scopus_publications_variants VALUES ('{primaryVariants[i]}', '{secondaryVariants[i]}');"
            cursor.execute(query)
            connection.commit()
        except:
            pass