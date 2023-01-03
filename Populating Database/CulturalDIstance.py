from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from itertools import combinations
from statistics import mean

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

distances = []
coordinates = []
affilCountries = []

doi = '10.1016/j.scs.2022.104089'
authorsID = [author[0] for author in AbstractRetrieval(doi).authors]
for author in authorsID:
    affilCountries.append(AuthorRetrieval(author).affiliation_current[0][8])

geolocator = Nominatim(user_agent = 'PersonalProject')
for country in affilCountries:
    location = geolocator.geocode(country)
    coordinates.append((location.latitude, location.longitude))

locationsCombinations = list(combinations(coordinates, 2))

for combo in locationsCombinations:
    distances.append(distance(combo[0][0], combo[0][1], combo[1][0], combo[1][1]))

print(f'Minimum Distance: {min(distances)} km, Maximum Distance: {max(distances)} km, Average Distance: {mean(distances)} km')