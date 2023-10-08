from pybliometrics.scopus import AffiliationRetrieval
from fuzzywuzzy import fuzz

def getMostRecentProfile(first_date, seconnectiond_date):
    """Return the most recent date between two dates."""
    return max(first_date, seconnectiond_date, key=lambda x: x[::-1])


def get_organizations_duplicates(connection, cursor):

    ids = []
    names = []
    scopusIds = []
    addresses = []

    primaryVariants = []
    secondaryVariants = []

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

    for i in range(len(names)-1):
        for j in range(i+1, len(names)):
            
            if (((fuzz.ratio(names[i], names[j]) > 85) | (names[i] in names[j]) | (names[j] in names[i])) 
                & (addresses[i] == addresses[j])):
                
                first_date = AffiliationRetrieval(int(scopusIds[i])).date_created
                second_date = AffiliationRetrieval(int(scopusIds[j])).date_created

                if (getMostRecentProfile(first_date, second_date) == first_date):
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
            query = f"INSERT INTO scopus_organizations_variants VALUES ('{primaryVariants[i]}', '{secondaryVariants[i]}');"
            cursor.execute(query)
            connection.commit()
        except:
            pass
