import pandas as pd
from google_places_api import GooglePlacesAPI
import time
import random

# Initialize the Google Places API client
places_api = GooglePlacesAPI()

# Read the original CSV file
df = pd.read_csv('hong_kong_restaurants_data.csv')

# Create a new DataFrame to store the enhanced data
enhanced_df = df.copy()

# Add new columns for the Google Places data
new_columns = ['google_name', 'google_address', 'maps_url', 'rating', 
               'user_ratings_count', 'phone', 'website', 'price_level', 
               'latitude', 'longitude', 'distance_meters']

for column in new_columns:
    enhanced_df[column] = None

# Process each restaurant
for index, row in df.iterrows():
    print(f"\nProcessing {index + 1}/{len(df)}: {row['Title']}")
    
    try:
        # Get restaurant details from Google Places API
        details = places_api.get_restaurant_details(
            restaurant_name=row['Title'],
            location=row['Address']
        )
        
        if details:
            # Update the enhanced DataFrame with the new details
            enhanced_df.at[index, 'google_name'] = details.get('name')
            enhanced_df.at[index, 'google_address'] = details.get('address')
            enhanced_df.at[index, 'maps_url'] = details.get('maps_url')
            enhanced_df.at[index, 'rating'] = details.get('rating')
            enhanced_df.at[index, 'user_ratings_count'] = details.get('user_ratings_count')
            enhanced_df.at[index, 'phone'] = details.get('phone')
            enhanced_df.at[index, 'website'] = details.get('website')
            enhanced_df.at[index, 'price_level'] = details.get('price_level')
            
            # Extract latitude and longitude if location data exists
            if details.get('location'):
                enhanced_df.at[index, 'latitude'] = details['location'].get('latitude')
                enhanced_df.at[index, 'longitude'] = details['location'].get('longitude')
            
            enhanced_df.at[index, 'distance_meters'] = details.get('distance_meters')
            
            print(f"Successfully found details for: {details.get('name')}")
        else:
            print(f"No details found for: {row['Title']}")
    
    except Exception as e:
        print(f"Error processing {row['Title']}: {str(e)}")
    
    # Add a random delay between requests to avoid hitting rate limits
    time.sleep(random.uniform(1, 3))
    
    # Save progress after every 10 restaurants
    if (index + 1) % 10 == 0:
        enhanced_df.to_csv('hong_kong_restaurants_enhanced.csv', index=False)
        print(f"Progress saved at restaurant {index + 1}")

# Save the final results
enhanced_df.to_csv('hong_kong_restaurants_enhanced.csv', index=False)
print("\nProcessing complete! Results saved to hong_kong_restaurants_enhanced.csv") 