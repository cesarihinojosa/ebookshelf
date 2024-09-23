from bs4 import BeautifulSoup
import requests
import re
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO,  # Set the lowest level of messages to log (DEBUG and above)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Custom format for log messages
    filename='logs/ebookshelf.log',  # Log messages to this file (omit this argument to log to console)
    filemode='a'  # 'w' for overwriting the log file, 'a' for appending
)

def get_books():

    logging.info("About to execute function get_books()")

    start = 1
    current = start
    end = 5000
    books = []
    small_images = []

    while current < end:

        link = f"https://www.goodreads.com/review/list/144045223-maria-reyna?page={current}&shelf=read&view=table"
        current += 1
        headers = { # necessary to imitate a human
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.3'
        }
        response = requests.get(link, headers=headers) # sending off request

        if response.status_code == 200: # catching an error if bad request
            logging.info(f"Successfully retrieved webpage #{current - 1}")
            webpage = response.text
            webpage = BeautifulSoup(webpage, "html.parser")
            table = webpage.find("table", id="books")

            if table:
                rows = table.find_all('tr')
                rows = rows[1:]
                for row in rows:
                    # Find all <td> elements with class 'field title'
                    cover = row.find('td', class_='field cover')
                    if cover:
                        img_tag = cover.find("img")
                        if img_tag and img_tag.has_attr('src'):
                            img_src = img_tag['src']
                            small_images.append(img_src)
                        else:
                            logging.error("No image tag or 'src' found.")
                    else:
                        logging.error("No 'td' with class 'field cover' found.")
            else:
                logging.error("Table with id 'books' NOT found!")
        else:
            logging.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")

        if len(rows) < 2: # if there are no books on page
            break

    pattern = r"/books/(\d+[a-zA-Z]/\d+)" 
    large_image_codes = []
    for image in small_images: # getting the ID from small image url
        match = re.search(pattern, image)
        if match:
            result = match.group(1)
            large_image_codes.append(result)
        else:
            logging.error("No match found during regex")

    # creating the new url for larger images
    large_images = ["https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/" + image + ".jpg" for image in large_image_codes]

    return large_images