import pandas as pd
import json

excelData = pd.read_excel('CulturalMap.xls')
dfData = pd.DataFrame(excelData, columns=[
                      'Country', 'Survival', 'Traditional'])

countries = dfData['Country']
survival = dfData['Survival']
traditional = dfData['Traditional']

culturalMap = {}

for i in range(len(countries)):
    culturalMap[countries[i]] = {
        "survival": survival[i],
        "traditional": traditional[i]
    }

with open("CulturalMap.json", "w") as f:
    json.dump(culturalMap, f, indent=4)
