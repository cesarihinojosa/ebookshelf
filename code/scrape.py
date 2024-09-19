from bs4 import BeautifulSoup
import requests
import re

def get_books():
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
            webpage = response.text
            webpage = BeautifulSoup(webpage, "html.parser")
            table = webpage.find("table", id="books")

            if table:
                rows = table.find_all('tr')
                for row in rows:
                    # Find all <td> elements with class 'field title'
                    cover = row.find('td', class_='field cover')
                    if cover:
                        img_tag = cover.find("img")
                        if img_tag and img_tag.has_attr('src'):
                            img_src = img_tag['src']
                            small_images.append(img_src)
                        else:
                            print("No image tag or 'src' found.")
                    else:
                        print("No 'td' with class 'field cover' found.")
            else:
                print("Table with id 'books' NOT found!")
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

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
            print("No match found")

    # creating the new url for larger images
    large_images = ["https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/" + image + ".jpg" for image in large_image_codes]

    return large_images