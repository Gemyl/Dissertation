import s2

metadata = s2.api.get_paper('10.1038/nrn3241', return_json=True)

for i in range(len(metadata['topics'])):
    print(metadata['topics'][i]['topic'])

# KEYS
# abstract
# arxivId
# authors
# citationVelocity
# citations
# corpusId
# doi
# fieldsOfStudy
# influentialCitationCount
# is_open_access
# is_publisher_licensed
# paperId
# references
# title
# topics
# url
# venue
# year