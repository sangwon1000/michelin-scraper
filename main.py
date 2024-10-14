import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

# Base URL for the Michelin Guide website with pagination
base_url = "https://guide.michelin.com/en/restaurants/page/{}"

# Start at page 1
page = 1

# Set to store unique restaurant URLs and names
seen = set()

# Counter for total restaurants found
total_restaurants = 0

# Get today's date in YYYY-MM-DD format
today_date = datetime.now().strftime("%Y-%m-%d")

# Create a CSV file with today's date in the file name
csv_filename = f'michelin_restaurants_{today_date}.csv'

# Open the CSV file to save the data
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Restaurant Name', 'Restaurant URL'])  # CSV header

    # Loop until there are no more restaurant results
    while True:
        # Fetch and parse the current page
        url = base_url.format(page)
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}, status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
    
        stats_element = soup.find('div', class_='search-results__stats')
        
        if stats_element:
            # Extract the text inside the <h1> tag
            total_restaurants_text = stats_element.find('h1').get_text(strip=True)
            
            # Extract the number (e.g., '1-20 of 17,328 Restaurants')
            expected_total = total_restaurants_text.split('of')[-1].strip().split()[0].replace(',', '')
            expected_total = int(expected_total)
            print(f"Total Number of Restaurants: {expected_total}")
        else:
            print("Failed to find the total number of restaurants.")

        # Find all restaurant links
        restaurants = soup.find_all('a', href=True)
        
        if not restaurants:
            print(f"No more restaurants found on page {page}. Stopping.")
            break  # Stop if no restaurants are found on the current page
        
        # Loop through the links and filter valid restaurants
        for restaurant in restaurants:
            href = restaurant['href']
            name = restaurant.get_text(strip=True)
            
            # Check if it's a valid restaurant link and has a non-empty name
            if '/restaurant/' in href and name and name != "Reserve a table":
                # Avoid duplicates by checking if we've already seen this href
                if href not in seen:
                    seen.add(href)  # Add to the set to prevent future duplicates
                    total_restaurants += 1  # Increment the restaurant count
                    full_url = f"https://guide.michelin.com{href}"
                    print(f"Restaurant: {name}, URL: {full_url}")
                    
                    # Write the restaurant name and URL to the CSV file
                    writer.writerow([name, full_url])
        
        # Sleep for a few seconds to avoid overloading the website
        time.sleep(2)  # Adjust the sleep duration as necessary

        # Move to the next page
        page += 1

# Final validation check
print(f"\nTotal Restaurants Scraped: {total_restaurants}")
if total_restaurants == expected_total:
    print("Success! The total number of restaurants matches the expected count of 17,336.")
else:
    print(f"Warning: The total number of restaurants ({total_restaurants}) does not match the expected count of 17,336.")
