import crossref_commons.retrieval as ret
import crossref_commons.relations as rel

pub = ret.get_publication_as_json('10.1016/j.softx.2019.100263')

for key in pub.keys():
    print(key)

######### Retrieval ########
# KEYS (pub)
# indexed: <class 'dict'>
# reference-count: <class 'int'>
# publisher: <class 'str'>
# issue: <class 'str'>
# license: <class 'list'>
# content-domain: <class 'dict'>
# short-container-title: <class 'list'>
# published-print: <class 'dict'>
# DOI: <class 'str'>
# type: <class 'str'>
# created: <class 'dict'>
# page: <class 'str'>
# source: <class 'str'>
# is-referenced-by-count: <class 'int'>
# title: <class 'list'>
# prefix: <class 'str'>
# volume: <class 'str'>
# author: <class 'list'>
# member: <class 'str'>
# published-online: <class 'dict'>
# reference: <class 'list'>
# container-title: <class 'list'>
# original-title: <class 'list'>
# language: <class 'str'>
# link: <class 'list'>
# deposited: <class 'dict'>
# score: <class 'int'>
# resource: <class 'dict'>
# subtitle: <class 'list'>
# short-title: <class 'list'>
# issued: <class 'dict'>
# references-count: <class 'int'>
# journal-issue: <class 'dict'>
# alternative-id: <class 'list'>
# URL: <class 'str'>
# relation: <class 'dict'>
# ISSN: <class 'list'>
# issn-type: <class 'list'>
# subject: <class 'list'>
# published: <class 'dict'>

# KEYS (indexed)
# date-parts
# date-time
# timestamp

# KEYS (content-domain)
# domain
# crossmark-restriction

# KEYS (published-print)
# date-parts

# KEYS (created)
# date-parts
# date-time
# timestamp

# KEYS (published-online)
# date-parts

# KEYS (deposited)
# date-parts
# date-time
# timestamp

# KEYS (resource)
# primary

# KEYS (issued)
# date-parts

# KEYS (journal-issue)
# issue
# published-print

# KEYS (resource)
# pdate-parts


####### Relations #######
# Related DOIs