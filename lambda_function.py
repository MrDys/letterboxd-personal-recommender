import urllib.request
from bs4 import BeautifulSoup as soup
import time
import json

# Parses out the id, link, name, rating, and heart status for a user's movies
def parse_page(page_html):
    movies = []
    page_soup = soup(page_html, 'html.parser')

    for id in page_soup.find_all('li', class_ = 'poster-container'):
        identifier = id.contents[1]['data-film-id']
        link = id.contents[1]['data-target-link']
        name  = id.contents[1].contents[1]['alt']
        try:
            rating = [i.split('rated-')[1] for i in id.contents[3].contents[1].attrs['class'] if i.startswith('rated-')][0]
        except IndexError:
            rating = 0
        try:
            if id.contents[3].contents[3] != '':
                heart = 1
        except IndexError:
            heart = 0

        movie = {
            'id': int(identifier),
            'name': name,
            'url': link,
            'rating': int(rating),
            'heart': heart
        }

        movies.append(movie)
    
    return movies

# Parses out the last page number of the user
def get_last_page(page_html):
    page_soup = soup(page_html, 'html.parser')
    page_links = page_soup.find_all('li', class_ = 'paginate-page')

    if not page_links:
        return 0

    last_page = page_links[-1].contents[0].get_text()

    return last_page

def lambda_handler(event, context):
    # Set up variables and grab the initial page
    user = event['queryStringParameters']['user']
    url = 'https://letterboxd.com/' + user + '/films/'

    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    page_html = response.read()

    # Parse the page and also parse out the last page number
    movies  = parse_page(page_html)
    last_page = get_last_page(page_html)

    # If there's only one page, return
    if int(last_page) == 0:
        return json.dumps(movies)

    # Loop through the rest of the page parsing and adding to the array
    for page in range(2, int(last_page) + 1):
        url = 'https://letterboxd.com/' + user + '/films/page/' + str(page)
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        page_html = response.read()

        time.sleep(5)

        movies += parse_page(page_html)
    
    return json.dumps(movies)


    