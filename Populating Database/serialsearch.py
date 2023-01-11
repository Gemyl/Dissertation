from pybliometrics.scopus import SerialSearch

inputDic = {}
inputDic['title'] = input('Enter title: ')
inputDic['issn'] = input('Enter issn: ')
inputDic['pub'] = input('Enter publication: ')
inputDic['subj'] = input('Enter subject: ')
inputDic['subjCode'] = input('Enter Subject Code: ')
inputDic['content'] = input('Enter content: ')
inputDic['oa'] = input('Enter open access (yes/no): ')

for key in inputDic.keys():
    if key == ' ':
        del inputDic[key]

print(inputDic)

res = SerialSearch(inputDic)
print(res)