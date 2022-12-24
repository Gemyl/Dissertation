from ScopusQueries import get_author_degrees_Scopus
import json

authorInfor = get_author_degrees_Scopus('57217424609')

for key in authorInfor['author-retrieval-response'][0]['author-profile'].keys():
    print(key)