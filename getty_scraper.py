import requests
import os
import time
import re
from unidecode import unidecode
from bs4 import BeautifulSoup

# Set the user agent string
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Read the list of search terms from the list.txt file
with open('list.txt', 'r') as f:
    search_terms = f.read().splitlines()
    
# Prompt the user for the number of pages to scrape
pages_to_scrape = input("For all search terms, how many pages should the script scrape? ")
pages_to_scrape = int(pages_to_scrape)

# Create a new directory called "output"
os.makedirs("output", exist_ok=True)

# Iterate over each search term
for search_term in search_terms:
    print(f"Searching for {search_term}...")

    # Set the initial page number to 1
    page_number = 1

    # Set a flag to indicate whether we've reached the last page
    last_page = False

    # Loop until we reach the last page or until we have scraped the required number of pages
    while page_number <= pages_to_scrape and not last_page:
        # Build the URL for the current page
        url = f"https://www.gettyimages.com/photos/{search_term}?assettype=image&license=rf&alloweduse=availableforalluses&family=creative&phrase={search_term}&sort=mostpopular&numberofpeople=none&page={page_number}"

        # Send a request to the URL and get the HTML response
        response = requests.get(url, headers=headers)
        html = response.text

        # Print the HTTP status code
        print(f"HTTP status code: {response.status_code}")

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the h1 header
        h1 = soup.find('h1')

        # Check if the h1 header is "Oops! We can't find the page you're looking for."
        if h1 and h1.text == "Oops! We can't find the page you're looking for.":
            # Set the last_page flag to True
            last_page = True
        else:
            # Find all images with the class "MosaicAsset-module__thumb___yvFP5"
            images = soup.find_all('img', {'class': 'MosaicAsset-module__thumb___yvFP5'})

            # Print the images variable
            print(f"Images: {images}")

            # If there are images, create a new directory for the search term and save the images
            if images:
                # Create a new directory inside the output folder
                dir_name = f"output/{search_term}"
                os.makedirs(dir_name, exist_ok=True)
                for image in images:
                    image_url = image['src']
                    response = requests.get(image_url)
                
                    # Replace non-ASCII characters with ASCII equivalents
                    alt = unidecode(image['alt'])

                    # Replace invalid characters with underscores
                    alt = re.sub(r'[^\w., ]', '_', alt)
               
                    # Replace "/" with a space
                    alt = re.sub(r'/', ' ', alt)
            
                    # Replace underscores followed by spaces with just spaces
                    alt = re.sub(r'_ ', ' ', alt)

                    # Replace double underscores with a single underscore
                    alt = re.sub(r'__+', '_', alt)
            
                    # Replace all underscores with a space
                    alt = re.sub(r'_', ' ', alt)

                    # Replace double spaces with a single space
                    alt = alt.replace('  ', ' ')

                    # Keep only the last period in the file name
                    alt = alt.rsplit('.', 1)[0]
                    
                    # Truncate the alt variable to a maximum length of 250 characters
                    alt = alt[:250]

                    # Save the image to the output folder
                    with open(f"{dir_name}/{alt}.jpg", 'wb') as f:
                        f.write(response.content)
            else:
                print(f"No images found for {search_term} on page {page_number}")

            # Check if there is a next page
            next_page = soup.find('button', {'class': 'PaginationRow-module__button___QQbMu PaginationRow-module__nextButton___gH3HZ'})
            if next_page:
                page_number += 1
            else:
                last_page = True

# Pause for a few seconds before making the next request
        time.sleep(5)

print("Done!")