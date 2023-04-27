# from tqdm import tqdm
# from geopy.geocoders import Nominatim
# from itertools import combinations
# from math import radians, sin, cos, sqrt, atan2
# from statistics import mean
# from fuzzywuzzy import fuzz
# import pandas as pd
# import numpy as np

# # organization type indexing
# orgTypeDict = {'Academic': 0,
#                'Government': 1,
#                'Business': 2,
#                'International': 3,
#                'Non-profit': 4,
#                'Association': 5}

# # matrix with organizational distances
# orgDistMap = [[1, 3, 5, 4, 3],
#               [3, 1, 5, 3, 4],
#               [5, 5, 1, 5, 5],
#               [4, 3, 5, 1, 4],
#               [3, 4, 5, 4, 1]]

# uniqueDois = []
# affiliationsType1 = []
# affiliationsType2 = []
# affiliationsAddresses = []
# affiliationsCities = []
# affiliationsCountries = []
# type1Group = []
# type2Group = []
# addressesGroup = []
# citiesGroup = []
# countriesGroup = []

# # get geographical distances
# def getGeoDistance(lat1, lon1, lat2, lon2):
#     # Convert latitude and longitude to radians
#     lat1 = radians(lat1)
#     lon1 = radians(lon1)
#     lat2 = radians(lat2)
#     lon2 = radians(lon2)

#     # Apply the Haversine formula
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1
#     a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     # Radius of Earth in kilometers
#     r = 6371

#     # Return the distance in kilometers
#     return c * r


# # calculating distances and proximities
# print('Calculating distances and proximities ...')
# distTemp = []
# distances = []
# cityCoord = []
# culturalDistancesGrp = []

# for k in tqdm(range(len(uniqueDois))):

#     try:
#         # calculating goegraphical distances
#         geolocator = Nominatim(user_agent='PersonalProject')
#         # only one organization affiliated with a publication
#         if len(affiliationsCities[k]) == 1:
#             minGeographicalDistance = str(0)
#             maxGeographicalDistance = str(0)
#             avgGeographicalDistance = str(0)
#             minOrganizationalDistance = str(1)
#             maxOrganizationalDistance = str(1)
#             avgOrganizationalDistance = str(1)
#             minCulturalDistance = str(0)
#             maxCulturalDistance = str(0)
#             avgCulturalDistance = str(0)

#         else:
#             # finding all the possible pairs between affiliated organizations cities
#             for city in affiliationsCities[k]:
#                 location = geolocator.geocode(city)
#                 cityCoord.append((location.latitude, location.longitude))

#             combos = list(combinations(cityCoord, 2))

#             # calculating the distance for each pair of organizations
#             for combo in combos:
#                 try:
#                     distances.append(
#                         getGeoDistance(combo[0][0], combo[0][1], combo[1][0], combo[1][1]))

#                     minGeographicalDistance = str(min(distances))
#                     maxGeographicalDistance = str(max(distances))
#                     avgGeographicalDistance = str(mean(distances))

#                 except Exception as err:
#                     print(str(err))
#                     minGeographicalDistance = str(9999)
#                     maxGeographicalDistance = str(9999)
#                     avgGeographicalDistance = str(9999)

#             # calculating organizational distances
#             if 'Other' not in affiliationsType1[k]:
#                 for i in range(len(affiliationsType1[k])-1):
#                     for j in range(i+1, len(affiliationsType1[k])):
#                         index1 = orgTypeDict[affiliationsType1[k][i]]
#                         index2 = orgTypeDict[affiliationsType1[k][j]]
#                         dist = orgDistMap[index1][index2]
#                         distTemp.append(dist)

#                 minOrganizationalDistance = str(min(distTemp))
#                 maxOrganizationalDistance = str(max(distTemp))
#                 avgOrganizationalDistance = str(mean(distTemp))

#             else:
#                 minOrganizationalDistance = str(9999)
#                 maxOrganizationalDistance = str(9999)
#                 avgOrganizationalDistance = str(9999)

#             # Load cultural map data into a DataFrame
#             culturalMap = pd.read_excel(
#                 "Populating Database\DBs Populators\CulturalDistances\CulturalMap.xls")
#             dfCulturalMap = pd.DataFrame(
#                 culturalMap, columns=['Country', 'Survival', 'Traditional'])

#             # Compute cultural distances for each pair of countries in affiliationsCountries[k]
#             culturalDistancesGrp = []
#             for i in range(len(affiliationsCountries[k]) - 1):
#                 for j in range(i + 1, len(affiliationsCountries[k])):
#                     firstCountry = None
#                     secondCountry = None

#                     for z in range(len(dfCulturalMap)):
#                         if ((dfCulturalMap.loc[z, 'Country'] == affiliationsCountries[k][i]) |
#                                 (dfCulturalMap.loc[z, 'Country'] in affiliationsCountries[k][i]) |
#                                 (affiliationsCountries[k][i] in dfCulturalMap.loc[z, 'Country']) |
#                                 (fuzz.ratio(dfCulturalMap.loc[z, 'Country'], affiliationsCountries[k][i]) > 90)):
#                             firstCountry = z

#                         if ((dfCulturalMap.loc[z, 'Country'] == affiliationsCountries[k][j]) |
#                                 (dfCulturalMap.loc[z, 'Country'] in affiliationsCountries[k][j]) |
#                                 (affiliationsCountries[k][j] in dfCulturalMap.loc[z, 'Country']) |
#                                 (fuzz.ratio(dfCulturalMap.loc[z, 'Country'], affiliationsCountries[k][j]) > 90)):
#                             secondCountry = z

#                         if firstCountry is not None and secondCountry is not None:
#                             break

#                     if firstCountry is None or secondCountry is None:
#                         continue

#                     culturalDistance = np.linalg.norm(dfCulturalMap.loc[firstCountry, ['Survival', 'Traditional']] -
#                                                       dfCulturalMap.loc[secondCountry, ['Survival', 'Traditional']])
#                     culturalDistancesGrp.append(culturalDistance)

#             # Compute summary statistics of cultural distances
#             if len(culturalDistancesGrp) > 0:
#                 minCulturalDistance = min(culturalDistancesGrp)
#                 maxCulturalDistance = max(culturalDistancesGrp)
#                 avgCulturalDistance = np.mean(culturalDistancesGrp)
#             else:
#                 minCulturalDistance = str(9999)
#                 maxCulturalDistance = str(9999)
#                 avgCulturalDistance = str(9999)

#             # Insert computed distances into database
#             query = f"INSERT INTO scopus_distances VALUES ('{uniqueDois[k]}',{citationsCount[k]},{authorsNumber[k]}, \
#                     {affiliationsNumber[k]},{minGeographicalDistance},{maxGeographicalDistance},{avgGeographicalDistance}, \
#                     {minOrganizationalDistance},{maxOrganizationalDistance},{avgOrganizationalDistance},{minCulturalDistance}, \
#                     {maxCulturalDistance},{avgCulturalDistance});"
#             cursor.execute(query)
#             connection.commit()

#         distTemp = []
#         distances = []
#         cityCoord = []
#         culturalDistancesGrp = []

#     except Exception as err:
#         print(str(err))
#         continue