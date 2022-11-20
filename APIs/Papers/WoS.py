from wos.client import WosClient

with WosClient() as wos:
    wos.connect()
    data = wos.search('10.1016/j.gloenvcha.2020.102194')