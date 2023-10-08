def get_safe_attribute(obj, attribute, attributeType):
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

        
def build_keywords_query(keywords, booleans):
    keywordsList = '('
    for i in range(len(keywords)):
        if i == len(keywords)-1:
            keywordsList = keywordsList + '{' + keywords[i] + '}'
        else:
            keywordsList = keywordsList + '{' + keywords[i] + '} ' + booleans[i]

    keywordsList = keywordsList + ')'
    keywords = keywordsList
    return keywords


def get_string_from_list(list):
    if list != None:
        string = ', '.join([str(i).lower() for i in list])
    else:
        string = ' '
    return string


def get_sql_syntax(string):
    if string != None:
        return string.replace("\'", " ")
    else:
        return "-"


def remove_common_words(abstract, commonWords):
    abstractList = abstract.split(" ")
    abstractString = " ".join(
        [word for word in abstractList if word.lower() not in commonWords])
    return abstractString


def get_affiliations_ids(affiliations):
    if affiliations != None:
        return [affil for affil in affiliations.split(";")]
    else:
        return "-"