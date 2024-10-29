import requests
import os
from dotenv import load_dotenv

class GooglePlacesAPI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://places.googleapis.com/v1/places"

    def get_place_id(self, restaurant_name, location):
        """
        Get the place ID for a restaurant using Google Places API Autocomplete (New).
        
        Args:
        restaurant_name (str): Name of the restaurant
        location (str): Text-based location (e.g., "Hong Kong", "Seoul")
        
        Returns:
        dict: Place details including place ID, or None if not found
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'suggestions.placePrediction.place,suggestions.placePrediction.placeId,suggestions.placePrediction.structuredFormat,suggestions.placePrediction.distanceMeters'
        }
        
        data = {
            "input": f"{restaurant_name} {location}",
        }
        
        response = requests.post(f"{self.base_url}:autocomplete", json=data, headers=headers)
        if response.status_code != 200:
            print(response.json())
            print(f"Error: {response.status_code}")
            return None
        
        result = response.json()
        print(result)
        if 'suggestions' in result and result['suggestions']:
            place = result['suggestions'][0]['placePrediction']
            return {
                'place_id': place['placeId'],
                'name': place['structuredFormat']['mainText']['text'],
                'address': place['structuredFormat']['secondaryText']['text'],
                'distance_meters': place.get('distanceMeters')
            }
        else:
            print("No results found")
            return None

    def get_place_details(self, place_id):
        """
        Get detailed information about a place using its place ID.
        
        Args:
        place_id (str): The place ID obtained from get_place_id function
        
        Returns:
        dict: Detailed place information
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'id,displayName,formattedAddress,googleMapsUri,location,rating,userRatingCount,types,internationalPhoneNumber,websiteUri,priceLevel'
        }
        
        response = requests.get(f"{self.base_url}/{place_id}", headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None
        
        return response.json()

    def get_restaurant_details(self, restaurant_name, location):
        """
        Get both basic and detailed information about a restaurant.
        
        Args:
        restaurant_name (str): Name of the restaurant
        location (str): Text-based location
        
        Returns:
        dict: Combined basic and detailed restaurant information, or None if not found
        """
        place_details = self.get_place_id(restaurant_name, location)
        if not place_details:
            print("Restaurant not found")
            return None
            
        print(f"\nFound: {place_details['name']}")

        detailed_info = self.get_place_details(place_details['place_id'])
        if not detailed_info:
            print("Failed to fetch detailed information")
            return None
                
        return {
            'name': detailed_info.get('displayName', {}).get('text'),
            'address': detailed_info.get('formattedAddress'),
            'maps_url': detailed_info.get('googleMapsUri'),
            'location': detailed_info.get('location'),
            'rating': detailed_info.get('rating'),
            'user_ratings_count': detailed_info.get('userRatingCount'),
            'phone': detailed_info.get('internationalPhoneNumber'),
            'website': detailed_info.get('websiteUri'),
            'price_level': detailed_info.get('priceLevel'),
            'distance_meters': place_details.get('distance_meters')
        }

# # Keep the testing code separate
# if __name__ == "__main__":
#     # Initialize the API client
#     places_api = GooglePlacesAPI()
    
#     restaurant = 'Trattoria Felino'
#     location = 'Shop 3&4, GF, Pao Yip Building, 1-7 Ship Street, Wan Chai, Hong Kong, Hong Kong SAR China'
#     # restaurant = '돌다메'
#     # location = '제주 제주시 외도일동'
#     place_details = places_api.get_restaurant_details(restaurant, location)
#     print(place_details)

