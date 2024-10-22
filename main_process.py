import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_csv('michelin_restaurants_2024-10-18.csv')

# Filter restaurants where the URL includes "hong-kong"
hong_kong_restaurants = df[df['Restaurant URL'].str.contains('hong-kong-region', case=False, na=False)]

# Print the number of Hong Kong restaurants found
print(f"Number of Hong Kong restaurants: {len(hong_kong_restaurants)}")

# Show all the restaurants
print(hong_kong_restaurants)

# Initialize a list to store restaurant data
restaurant_data = []

for index, row in hong_kong_restaurants.iterrows():
    print(f"Processing restaurant {index + 1} of {len(hong_kong_restaurants)}")
    print(f"URL: {row['Restaurant URL']}")
    
    url = row['Restaurant URL']
    
    # Open the URL using requests
    response = requests.get(url)
    # print(response.text)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the required information
    title = soup.find('h1', class_='data-sheet__title')
    address = soup.find_all('div', class_='data-sheet__block--text')[0]  # First occurrence for address
    price_cuisine_div = soup.find_all('div', class_='data-sheet__block--text')[1]  # Second occurrence for price and cuisine

    # Split the text to separate price and cuisine
    price_cuisine_text = price_cuisine_div.text.strip() if price_cuisine_div else 'N/A'
    price, cuisine = price_cuisine_text.split('·') if '·' in price_cuisine_text else (price_cuisine_text, 'N/A')

    # Extract cuisine from data attribute
    cuisine_data = soup.find('button', {'data-cooking-type': True})
    cuisine = cuisine_data['data-cooking-type'] if cuisine_data else cuisine.strip()

    description = soup.find('div', class_='data-sheet__description')
    services = soup.find('div', class_='restaurant-details__services')
    map_iframe = soup.find('iframe', class_='google-map__static')
    phone = soup.find('span', dir='ltr')
    website = soup.find('a', attrs={'data-event': 'CTA_website'})

    # Append the extracted information to the list
    restaurant_data.append({
        'Title': title.text.strip() if title else 'N/A',
        'Address': address.text.strip() if address else 'N/A',
        'Price': price.strip() if price else 'N/A',
        'Cuisine': cuisine,
        'Description': description.text.strip() if description else 'N/A',
        'Services': services.text.strip() if services else 'N/A',
        'Map Iframe URL': map_iframe['src'] if map_iframe else 'N/A',
        'Phone': phone.text.strip() if phone else 'N/A',
        'Website': website['href'] if website else 'N/A'
    })

# Convert the list of dictionaries to a DataFrame
restaurants_df = pd.DataFrame(restaurant_data)

# Output the DataFrame to a CSV file
restaurants_df.to_csv('hong_kong_restaurants_data.csv', index=False)
