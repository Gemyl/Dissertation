import requests
import json
baseURL = "http://api.elsevier.com/content/abstract/citations"
headers = {'Accept': 'application/json',
           'X-ELS-APIKey': '33a5ac626141313c10881a0db097b497'}
params = '?doi=10.1093/bjsw/bcaa237'

url = baseURL + params

resp = requests.get(url, headers=headers)
print(json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': ')))
