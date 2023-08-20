from fuzzywuzzy import fuzz

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

            if((ids[i] not in variants2Ids) & (fuzz.ratio(titles[i], titles[j]) > 85) 
               & (fuzz.ratio(abstracts[i], abstracts[j]) > 85) & (fuzz.ratio(keywords[i], keywords[j]) > 85) 
               & (fuzz.ratio(fields[i], fields[j]) > 85)):

                if (citationsCount[i] > citationsCount[j]):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])

                else:
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
                    break
                      
            else:
                break

    # Inserting duplicates in the SQL database
    for i in range(len(variants1Ids)):
        try:
            query = f"INSERT INTO scopus_publications_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
            cursor.execute(query)
            connection.commit()
        except:
            pass