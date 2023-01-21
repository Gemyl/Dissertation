from pybliometrics.scopus import AbstractRetrieval, AffiliationRetrieval
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim 
from itertools import combinations
from statistics import mean
from tqdm import tqdm

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


def geographical_distances(cities):

    minDist = []
    maxDist = []
    avgDist = []
    distances = []
    cityCoord = []

    for cityGrp in tqdm(cities):

        try:
            geolocator = Nominatim(user_agent = 'PersonalProject')
            for city in cityGrp:
                location = geolocator.geocode(city)
                cityCoord.append((location.latitude, location.longitude))

            combos = list(combinations(cityCoord, 2))

            for combo in combos:
                distances.append(distance(combo[0][0], combo[0][1], combo[1][0], combo[1][1]))
            
            minDist.append(str(min(distances)))
            maxDist.append(str(max(distances)))
            avgDist.append(str(mean(distances)))

            distances = []
            cityCoord = []

        except:
            minDist.append('-')
            maxDist.append('-')
            avgDist.append('-')

    return minDist, maxDist, avgDist


def organizational_distances(orgTypes1):

    minDist = []
    maxDist = []
    avgDist = []
    distTemp = []

    orgTypeDict = {'Academic':0,
                   'Government':1, 
                   'Business':2,
                   'International':3, 
                   'Non-profit':4, 
                   'Association':5}

    orgDistMap = [[1,3,5,4,3],
                  [3,1,5,3,4],
                  [5,5,1,5,5],
                  [4,3,5,1,4],
                  [3,4,5,4,1]]

    for orgs in orgTypes1:

        if 'Other' not in orgs:
            for i in range(len(orgs)-1):
                for j in range(i+1, len(orgs)):
                    index1 = orgTypeDict[orgs[i]]
                    index2 = orgTypeDict[orgs[j]]
                    dist = orgDistMap[index1][index2]
                    distTemp.append(dist)
            
            minDist.append(str(min(distTemp)))
            maxDist.append(str(max(distTemp)))
            avgDist.append(str(mean(distTemp)))

            distTemp = []
        
        else:
            minDist.append('0')
            maxDist.append('0')
            avgDist.append('0')
        
    
    return minDist, maxDist, avgDist