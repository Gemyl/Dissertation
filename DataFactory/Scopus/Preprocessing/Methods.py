def getSafeAttribute(obj, attribute, attributeType):
    try:
        if isinstance(obj, dict):
            value = obj.get(attribute)
            if((value == None) & (attributeType == "number")):
               value = 999999
            elif (obj.get(attribute) == None):
                value = "-"
        else:
            value = getattr(obj, attribute)
            if((value == None) & (attributeType == "number")):
               value = 999999
            elif (value == None):
                value = "-"

    except (AttributeError, KeyError):
        if attributeType == "number":
            value = 999999
        else:
            value = "-"
    
    return value

        
def buildKeywordsQuery(keywords, booleans):
    # keywords = keywords.split(', ')
    keywordsList = '('
    for i in range(len(keywords)):
        if i == len(keywords)-1:
            keywordsList = keywordsList + '{' + keywords[i] + '}'
        else:
            keywordsList = keywordsList + '{' + keywords[i] + '} ' + booleans[i]

    keywordsList = keywordsList + ')'
    keywords = keywordsList
    return keywords


def getStringFromList(list):
    if list != None:
        string = ', '.join([str(i).lower() for i in list])
    else:
        string = ' '
    return string


def getColumnLength(column, table, cursor):

    try:
        query = f"SELECT MAX(LENGTH({column})) FROM {table};"
        cursor.execute(query)
        resultSet = cursor.fetchall()

        if resultSet[0][0] != None:
            return resultSet[0][0]
        else:
            return 100
        
    except:
        return 100


def applySqlSyntax(string):
    if string != None:
        return string.replace("\'", " ")
    else:
        return "-"


def removeCommonWords(abstract, commonWords):
    abstractList = abstract.split(" ")
    abstractString = " ".join(
        [word for word in abstractList if word.lower() not in commonWords])
    return abstractString


def getAffiliationsIds(affiliations):
    if affiliations != None:
        return [affil for affil in affiliations.split(";")]
    else:
        return "-"