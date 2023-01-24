import requests
import os
import time
import sys
import re
import hashlib
import random
import threading
from unidecode import unidecode
from bs4 import BeautifulSoup

proxy_list = [
    "some-fake-ass-proxy.com:8080",
    "some-other-fake-ass-proxy.com:1993"
]

last_proxy: str = None


def next_proxy():
    global last_proxy
    if len(proxy_list) <= 0:
        return None

    proxy = random.choice(proxy_list)
    if proxy == last_proxy:
        return next_proxy()

    last_proxy = proxy

    return {
        "http": proxy,
        "https": proxy
    }


# Set the user agent string
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Read the list of search terms from the list.txt file
with open('list.txt', 'r') as f:
    search_terms = f.read().splitlines()

# Prompt the user for the number of pages to scrape
pages_to_scrape = input("For all search terms, how many pages should the script scrape? ")
pages_to_scrape = int(pages_to_scrape)

# Iterate over each search term
for search_term in search_terms:
    search_term = search_term.strip().lower()
    print(f"Searching for {search_term}...")

    # Set the initial page number to 1
    page_number = 1

    # Set a flag to indicate whether we've reached the last page
    last_page = False

    name = search_term.replace(':', '_')
    dir_name = os.path.abspath(f"./output/{name}")

    if os.path.isdir(dir_name):
        print(f"Directory exists, skipping '{search_term}'...")
        continue

    # create directory for image output
    os.makedirs(dir_name, exist_ok=True)

    # retries on search term before abandoning
    retries = 0

    # Loop until we reach the last page or until we have scraped the required number of pages
    while page_number <= pages_to_scrape and not last_page:
        # Build the URL for the current page
        url = f"https://www.gettyimages.com/photos/{search_term}?assettype=image&license=rf&alloweduse=availableforalluses&family=creative&phrase={search_term}&sort=mostpopular&numberofpeople=none&page={page_number}"

        try:
            # Send a request to the URL and get the HTML response using the selected proxy
            next = next_proxy()
            if next is not None:
                print("Using", next['http'], "as next proxy...")

            response = requests.get(url, headers=headers, proxies=next, timeout=5)
            html = response.text
        except:
            print("Retrying...")
            retries = retries + 1
            if retries >= len(proxy_list):
                print("Failed to fetch images...")
                sys.exit()
            else:
                continue

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
            print(f"Found images: {len(images)}")

            # If there are images, create a new directory for the search term and save the images
            if images:
                sub_lists = [images[x:x+10] for x in range(0, len(images), 10)]
                threads = []

                def do_download(images):
                    for image in images:
                        image_url = image['src']
                        response = requests.get(image_url, proxies=next)

                        # Replace non-ASCII characters with ASCII equivalents
                        alt = unidecode(image['alt'])

                        # Replace invalid characters
                        alt = re.sub(r'[^\w.:, ]', '_', alt)
                        alt = re.sub(r'/', ' ', alt)
                        alt = re.sub(r'_ ', ' ', alt)
                        alt = re.sub(r'__+', '_', alt)
                        alt = re.sub(r'_', ' ', alt)
                        alt = alt.replace('  ', ' ')
                        alt = alt.replace(':', '_')
                        alt = alt.rsplit('.', 1)[0]

                        name = f"{time.time_ns}.{alt}"
                        name = hashlib.sha256(name.encode()).hexdigest()

                        # Save alt text to file next to image
                        with open(f"{dir_name}/{name}.txt", "w+") as f:
                            f.write(alt)
                            f.close()

                        # Save the image to the output folder
                        with open(f"{dir_name}/{name}.jpg", 'wb') as f:
                            f.write(response.content)
                            f.close()

                print(f"Started {len(sub_lists)} threads...")
                for sub_list in sub_lists:
                    thread = threading.Thread(
                        target=lambda: do_download(sub_list))
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
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
