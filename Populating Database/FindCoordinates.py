from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent='PersonalProject')

address = "1600 Amphitheatre Parkway, Mountain View, CA"

location = geolocator.geocode(address)

print(location.latitude, location.longitude)