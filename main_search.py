import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import random
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options

# Load the CSV file into a DataFrame
df = pd.read_csv('hong_kong_restaurants_data_with_coordinates.csv')

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--window-size=1920,1080")  # Set window size to ensure proper rendering

# Initialize the Chrome WebDriver with headless options
driver = webdriver.Chrome(options=chrome_options)  # or use webdriver.Firefox() if using Firefox

# Open Google Maps
driver.get("https://www.google.com/maps")

# Function to extract coordinates from URL
def extract_coordinates(url):
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

# Function to perform WebDriverWait with retries
def wait_for_element(driver, locator, timeout=10, max_retries=1):
    for retry in range(max_retries):
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            print(f"Timeout occurred. Retry {retry + 1}/{max_retries}")
            if retry == max_retries - 1:
                raise
            time.sleep(2)

# Function to perform WebDriverWait for clickable elements with retries
def wait_for_clickable(driver, locator, timeout=10, max_retries=1):
    for retry in range(max_retries):
        try:
            return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            print(f"Timeout occurred. Retry {retry + 1}/{max_retries}")
            if retry == max_retries - 1:
                raise
            time.sleep(2)

# Loop through each restaurant in the DataFrame
for index, row in df.iterrows():
    # Check if data is already present
    if pd.notna(row.get('Lat_Name')) and pd.notna(row.get('Lng_Name')) and pd.notna(row.get('Share_URL')):
        continue  # Skip if data is already present

    name = row['Title']
    address = row['Address']
    
    try:
        # Search by name
        search_box = wait_for_element(driver, (By.ID, "searchboxinput"))
        search_box.clear()
        search_box.send_keys(name, " Hong Kong")
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3 + random.uniform(1, 3))  # Wait for results to load, with some randomness
        
        current_url = driver.current_url
        lat_name, lng_name = extract_coordinates(current_url)
        
        print(f"Coordinates for {name} (by name): Lat: {lat_name}, Lng: {lng_name}")

        # get share link
        share_button = wait_for_clickable(driver, (By.XPATH, "//button[@data-value='Share']"))
        share_button.click()

        share_link = wait_for_element(driver, (By.CSS_SELECTOR, "input.vrsrZe[readonly][type='text']"), timeout=30)
        share_url = share_link.get_attribute('value')
        print(f"Share link for {name}: {share_url}")

        # Store the share URL in the DataFrame
        df.at[index, 'Share_URL'] = share_url
        
        # Close the share dialog
        close_button = wait_for_clickable(driver, (By.XPATH, "//button[@aria-label='Close']"))
        close_button.click()
        
        time.sleep(1 + random.uniform(0.5, 1.5))  # Short pause after closing dialog
        
        # Search by address
        search_box = wait_for_element(driver, (By.ID, "searchboxinput"))
        search_box.clear()
        search_box.send_keys(address)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3 + random.uniform(1, 3))  # Wait for results to load, with some randomness
        
        current_url = driver.current_url
        lat_address, lng_address = extract_coordinates(current_url)
        
        print(f"Coordinates for {name} (by address): Lat: {lat_address}, Lng: {lng_address}")
        
        # Store the results in the DataFrame
        df.at[index, 'Lat_Name'] = lat_name
        df.at[index, 'Lng_Name'] = lng_name
        df.at[index, 'Lat_Address'] = lat_address
        df.at[index, 'Lng_Address'] = lng_address

    except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
        print(f"Error occurred for {name}: {str(e)}. Moving to the next restaurant.")
        driver.get("https://www.google.com/maps")
        continue

    # Save the updated DataFrame after each iteration
    df.to_csv('hong_kong_restaurants_data_with_coordinates.csv', index=False)

    time.sleep(2 + random.uniform(1, 2))  # Pause between iterations, with some randomness

# Close the browser
driver.quit()
