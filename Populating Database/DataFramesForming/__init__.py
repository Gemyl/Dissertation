from pybliometrics.scopus import AbstractRetrieval

def FindMaxNumAuthors(DOIs):
    removeDOIs = []
    maxAuthors = 0
    for i in range(len(DOIs)):
        try:
            numAuthors = len(AbstractRetrieval(DOIs[i]).authors)
            if (numAuthors > maxAuthors) & (numAuthors < 10):
                maxAuthors = len(AbstractRetrieval(DOIs[i]).authors)
        except:
            removeDOIs.append(DOIs[i])

    for i in range(len(removeDOIs)):
        DOIs.remove(removeDOIs[i])

    return maxAuthors, DOIs