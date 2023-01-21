def format_keywords(keywords):
    keywords = keywords.split(', ')
    keywordsList = '('
    for i in range(len(keywords)):
        if i == len(keywords)-1:
            keywordsList = keywordsList + '{' + keywords[i] + '}'
        else:
            keywordsList = keywordsList + '{' + keywords[i] + '} ' + 'OR '

    keywordsList = keywordsList + ')'
    keywords = keywordsList

    return keywords

def list_to_string(list):

    if list != None:

        string = ', '.join([str(i).lower() for i in list])
    else:
        string = ' '

    return string