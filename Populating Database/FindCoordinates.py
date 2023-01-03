from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent='PersonalProject')

address = "Greece"

location = geolocator.geocode(address)

print(location.latitude, location.longitude)