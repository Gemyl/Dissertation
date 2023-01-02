from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent='PersonalProject')

address = "9201 University City Blvd"

location = geolocator.geocode(address)

print(location.latitude, location.longitude)