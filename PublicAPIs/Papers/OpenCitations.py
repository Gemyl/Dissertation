import opencitingpy
import json

client = opencitingpy.client.Client()
metadata = client.get_metadata('10.1016/j.softx.2019.100263')
string = str(metadata[0]).replace('\'', '\"')
dictionary = json.loads(string)

for key in dictionary.keys():
    print(key)

# KEYS
# issue
# title
# citation_count
# year
# doi
# reference
# page
# citation
# source_title
# source_id
# author
# oa_link
# volume