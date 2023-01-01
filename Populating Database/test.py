# from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
# from DataRetrieving import get_DOIs

# keywords = str(input('Keywords: '))
# yearsRange = str(input('Years Range: '))
# subjects = input('Subjects: ').split(', ')

# parents = []
# authorsID = []
# papersOrgs = []
# authorsOrgs = []
# authorsOrgsID = []

# DOIs = get_DOIs(keywords, yearsRange, subjects)

# for DOI in DOIs:
#     tempOrgs = AbstractRetrieval(DOI).affiliation
#     for org in tempOrgs:
#         if org not in papersOrgs:
#             papersOrgs.append(org[0])
    
#     authors = AbstractRetrieval(DOI).authors
#     for author in authors:
#         authorID = author[0]
#         for org in AuthorRetrieval(authorID).affiliation_current:
#             if (org[0] not in papersOrgs) & (org[1] in papersOrgs):
#                 papersOrgs.append(org[0])
#         for org in AuthorRetrieval(authorID).affiliation_history:
#             if (org[0] not in papersOrgs) & (org[1] in papersOrgs):
#                 papersOrgs.append(org[0])


# for DOI in DOIs:
#     authors = AbstractRetrieval(DOI).authors
#     for author in authors:
#         authorID = AuthorRetrieval(author[0]).identifier
#         if authorID not in authorsID:
#             authorsID.append(authorID)
#             for org in AuthorRetrieval(authorID).affiliation_current:
#                 if AffiliationRetrieval(org[0]).identifier not in authorsOrgsID:
#                     authorsOrgs.append(org)
#                     authorsOrgsID.append(AffiliationRetrieval(org[0]).identifier)
#             for org in AuthorRetrieval(authorID).affiliation_history:
#                 if AffiliationRetrieval(org[0]).identifier not in authorsOrgsID:
#                     authorsOrgs.append(org)
#                     authorsOrgsID.append(AffiliationRetrieval(org[0]).identifier)


# for org in papersOrgs:
#     try:
#         index = authorsOrgsID.index(AffiliationRetrieval(org).identifier)
#         parents.append(authorsOrgs[index][6])
#     except:
#         parents.append(None)    


# for i in range(len(papersOrgs)):
#     print(str(papersOrgs[i]) + ', ' + str(parents[i]))

lst1 = [1,2,3,4]
lst2 = [1,2]
lst1 = [index for index in lst1 if index not in lst2]
print(lst1)