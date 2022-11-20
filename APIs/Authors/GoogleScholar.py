from scholarly import scholarly

author = scholarly.search_author_id('otjuGKYAAAAJ')

for key in author.keys():
    print(key)

# KEYS
# container type
# filled
# source
# scholar id
# url picture
# name
# affiliation
# email domain
# interests
# cited by