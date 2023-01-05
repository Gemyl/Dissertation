from pybliometrics.scopus import AbstractRetrieval, AffiliationRetrieval
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
from DataRetrieving import get_DOIs
from itertools import combinations
from statistics import mean
from tqdm import tqdm
import pandas as pd

def distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    # Apply the Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    # Return the distance in kilometers
    return c * r

minDist = []
maxDist = []
avgDist = []
countries = []
distances = []
coordinates = []
citationsCount = []
affilCountries = []
keywords = input('Keywords: ')
yearsRange = input('Years range: ')
subjects = input('Subjects: ').split(', ')

DOIs = get_DOIs(keywords,yearsRange, subjects)

for doi in tqdm(DOIs):
    citationsCount.append(AbstractRetrieval(doi).citedby_count)
    authorsID = [author[0] for author in AbstractRetrieval(doi).authors]
    for i in range(len(authorsID)):
        try:
            orgID = (AbstractRetrieval(doi).authors[i][4]).split(';')[0]
            affilCountries.append(AffiliationRetrieval(orgID).country)
        except:
            continue

    countries.append(affilCountries)

    geolocator = Nominatim(user_agent = 'PersonalProject')
    for country in affilCountries:
        location = geolocator.geocode(country)
        coordinates.append((location.latitude, location.longitude))

    locationsCombinations = list(combinations(coordinates, 2))

    for combo in locationsCombinations:
        distances.append(distance(combo[0][0], combo[0][1], combo[1][0], combo[1][1]))
    
    try:
        minDist.append(min(distances))
    except:
        minDist.append('-')

    try:    
        maxDist.append(max(distances))
    except:
        maxDist.append('-')

    try:
        avgDist.append(mean(distances))
    except:
        avgDist.append('-')
    
    distances = []
    coordinates = []
    affilCountries = []

print(len(DOIs))
print(len(citationsCount))
print(len(minDist))
print(len(maxDist))
print(len(avgDist))

cultDist = pd.DataFrame({'DOI':DOIs, 'Citations Count':citationsCount, 'Minimum Distance':minDist,
    'Maximum Distance':maxDist, 'Average Distance':avgDist, 'Countries':countries})

with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
    print(cultDist)
