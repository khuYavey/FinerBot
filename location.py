from geopy.geocoders import Nominatim


def analyze_location(latitude, longtitude):
    # Create a geolocator with SSL verification disabled
    geolocator = Nominatim(user_agent=__name__)


    location = geolocator.reverse((latitude, longtitude))
    if location:

        try:
            return " ".join([location.raw['address']['city'], location.raw['address']['borough'], location.raw['address']['road'], location.raw['address']['house_number']])
        except:
            return location.address


    # def get_location(lat, long):
    #     location = geocoder.google([lat, long], method='reverse')
    #     print(location.current_result)
