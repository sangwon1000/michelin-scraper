import requests
import os
from dotenv import load_dotenv

def get_place_id(restaurant_name, location):
    """
    Get the place ID for a restaurant using Google Places API Autocomplete (New).
    
    Args:
    restaurant_name (str): Name of the restaurant
    location (str): Text-based location (e.g., "Hong Kong", "Seoul")
    
    Returns:
    dict: Place details including place ID, or None if not found
    """
    load_dotenv()  # Load API key from .env file
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    base_url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'suggestions.placePrediction.place,suggestions.placePrediction.placeId,suggestions.placePrediction.structuredFormat,suggestions.placePrediction.distanceMeters'
    }
    
    data = {
        "input": f"{restaurant_name} {location}",
    }
    
    response = requests.post(base_url, json=data, headers=headers)
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

def get_place_details(place_id):
    """
    Get detailed information about a place using its place ID.
    
    Args:
    place_id (str): The place ID obtained from get_place_id function
    
    Returns:
    dict: Detailed place information
    """
    load_dotenv()  # Load API key from .env file
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    base_url = "https://places.googleapis.com/v1/places/"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'id,displayName,formattedAddress,googleMapsUri,location,rating,userRatingCount,reviews,types,internationalPhoneNumber,websiteUri,priceLevel'
    }
    
    response = requests.get(f"{base_url}{place_id}", headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None
    
    result = response.json()
    return result

if __name__ == "__main__":
    restaurant = 'tim ho wan'
    location = 'hong kong'
    place_details = get_place_id(restaurant, location)
    if place_details:
        print("Basic Place Details:")
        print(f"Place ID: {place_details['place_id']}")
        print(f"Name: {place_details['name']}")
        print(f"Address: {place_details['address']}")
        if place_details['distance_meters']:
            print(f"Distance: {place_details['distance_meters']} meters")
        
        print("\nFetching detailed information...")
        detailed_info = get_place_details(place_details['place_id'])
        if detailed_info:
            print("\nDetailed Place Information:")
            print(f"Name: {detailed_info.get('displayName', {}).get('text', 'N/A')}")
            print(f"Address: {detailed_info.get('formattedAddress', 'N/A')}")
            print(f"Google Maps Link: {detailed_info.get('googleMapsUri', 'N/A')}")
            print(f"Latitude: {detailed_info.get('location', {}).get('latitude', 'N/A')}")
            print(f"Longitude: {detailed_info.get('location', {}).get('longitude', 'N/A')}")
            print(f"Rating: {detailed_info.get('rating', 'N/A')}")
            print(f"User Ratings Count: {detailed_info.get('userRatingCount', 'N/A')}")
            print(f"Phone: {detailed_info.get('internationalPhoneNumber', 'N/A')}")
            print(f"Website: {detailed_info.get('websiteUri', 'N/A')}")
            print(f"Price Level: {detailed_info.get('priceLevel', 'N/A')}")
            
            print("\nReviews:")
            for review in detailed_info.get('reviews', [])[:3]:  # Limit to first 3 reviews
                print(f"- Rating: {review.get('rating', 'N/A')}")
                # print(f"  Text: {review.get('text', {}).get('text', 'N/A')[:100)}...")  # Truncate long reviews
                # print()
        else:
            print("Failed to fetch detailed information.")
