from scholarly import scholarly

query = scholarly.search_pubs('10.1016/j.gloenvcha.2020.102194')
first_pub_res = next(query)

print(len(first_pub_res['citedby_url']))

# KEYS
# container_type: <class 'str'>
# source: <enum 'PublicationSource'>
# bib: <class 'dict'>
# filled: <class 'bool'>
# gsrank: <class 'int'>
# pub_url: <class 'str'>
# author_id: <class 'list'>
# url_scholarbib: <class 'str'>
# url_add_sclib: <class 'str'>
# num_citations: <class 'int'>
# citedby_url: <class 'str'>
# url_related_articles: <class 'str'>
# eprint_url: <class 'str'>


# bib keys
# title: <class 'str'>
# author: <class 'list'>
# pub_year: <class 'str'>
# venue: <class 'str'>
# abstract: <class 'str'>