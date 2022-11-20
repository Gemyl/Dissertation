from requests import get
from json import loads

BaseURL = "https://api.datacite.org/dois/"
DoiURL = "10.5438/jwvf-8a66"
EndURL = "/activities"

url = BaseURL + DoiURL + EndURL

res = get(url)
metadata_txt = res.text
metadata_json = loads(metadata_txt)

data = metadata_json['data'][0]
meta = metadata_json['meta']
links = metadata_json['links']

attributes = data['attributes']
changes = attributes['changes']

for key in meta.keys():
    print(meta[key])

# KEYS
# Metadata: data, meta, links

# Data: id, type, attributes
# Meta: total, totalPages, page
# links: self

# Attributes: prov:wasGeneratedBy, prov:generatedAtTime, prov:wasDerivedFrom, prov:wasAttributedTo, action, version, changes

# Changes: dates, titles, creators, subjects, rights_list, descriptions, related_identifiers

# Dates: date, dateType, dateInformation
# Titles: lang, title, titleType
# Creators: name, nameType, givenName, familyName, affiliation, nameIdentifiers
# Subjects: subject
# Rigghts: rights, rightsUri, schemeUri, rightsIdentifier, rightsIdentifierScheme
# Descriptions: lang, description, descriptiontype
# Related Identifiers: schemeUri, schemeType, relationType, relatedIdentifier, resourceTypeGeneral, relatedIdentifierType, relatedMetadataScheme 