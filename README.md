# Getty Images Thumbnail Scraper - Python Script

Perfect scraper for AI model training, since you only need around 512x512. The thumbnails retrieved from gettyimages are close to that size.

This entire script was programmed by ChatGPT (AI Language Model) with a little bit of back and forth debugging also provided by ChatGPT.
You can try ChatGPT here: https://chat.openai.com/

# Installation requirements prior to using:

```
pip install requests
pip install unidecode
pip install bs4
```

# How to Use

Create a `list.txt` with your search terms. Each line should be a new term. This should be placed in the same folder.

Afer running the script, it'll ask you how many pages should be scraped for every search term. All images will be placed in separate folders within a newly created output folder.
