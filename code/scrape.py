from bs4 import BeautifulSoup
import requests

start = 1
current = start
end = 5000
titles = []

while current < end:

    link = f"https://www.goodreads.com/review/list/144045223-maria-reyna?page={current}&shelf=read&view=table"
    current += 1
    headers = { # necessary to imitate a human
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
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
                cells = row.find_all('td', class_='field title')
                for cell in cells:
                    # Find the <a> tag inside the <td>
                    link = cell.find('a')
                    
                    if link:
                        # Extract text attribute of the <a> tag
                        link_text = link.get_text(strip=True)
                        titles.append(link_text)
                    else:
                        print("No <a> tag found in this <td>.")
        else:
           print("Table with id 'books' NOT found!")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    if len(rows) < 2: # if there are no books on page
        break

print(titles)