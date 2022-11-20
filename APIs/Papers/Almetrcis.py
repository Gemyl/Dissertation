from requests import get
import json

api_link = "https://api.altmetric.com/v1/doi/"
doi = "10.1016/j.gloenvcha.2020.102194"

url = api_link + doi

req = get(url)
res = json.loads(req.text.encode('ascii', errors='ignore'))

for key in res.keys():
    print(key)

# KEYS
# title
# doi
# urn
# altmetric_jid
# issns
# journal
# cohorts
# context
# authors
# type
# pubdate
# altmetric_id
# schema
# is_oa
# publisher_subjects
# cited_by_posts_count
# cited_by_tweeters_count
# cited_by_msm_count
# cited_by_feeds_count
# cited_by_fbwalls_count
# cited_by_rdts_count
# cited_by_rh_count
# cited_by_wikipedia_count
# cited_by_policies_count
# cited_by_accounts_count
# last_updated
# score
# history
# url
# added_on
# published_on
# scopus_subjects
# readers
# readers_count
# images
# details_url