import requests
import re
import json
from bs4 import BeautifulSoup

pages_to_visit = []
visited_pages = []
seed = 'https://store.steampowered.com/'
api = 'https://store.steampowered.com/appreviews/{}?cursor=*&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=english&l=english&review_type=all&purchase_type=all&playtime_filter_min=0&playtime_filter_max=0&filter_offtopic_activity=1'

pages_to_visit.append(seed)
data = []

# main loop
while len(pages_to_visit) != 0:
    page = pages_to_visit.pop(0)
    raw_html = requests.get(page).content
    soup = BeautifulSoup(raw_html, 'html.parser')
    url = soup.find('meta', {'property' : 'og:url'})

    search = re.search('/app/', str(url))
    if search:
        data_obj = {}
        data_obj['reviews'] = []

        # if url is a game page, get the game id
        temp = str(url)[search.end():]
        delimiter = temp.find('/')
        data_obj['game_id'] = temp[:delimiter]

        # get the title of the game
        temp = temp[delimiter + 1:]
        delimiter = temp.find('/')
        data_obj['game_title'] = temp[:delimiter]

        # get the reviews
        reviews_html = requests.get(api.format(data_obj['game_id'])).json()['html']
        s = BeautifulSoup(reviews_html, 'html.parser')
        reviews = s.find_all('div', {'id': re.compile('^ReviewContentsummary[0-9]*$')})

        # extract data from every review
        for review in reviews:
            name_container = review.find('div', {'class' : 'persona_name'})
            data_obj['reviews'].append({
                'username' : name_container.find('a').text,
                'comment' : review.find('div', {'class' : 'content'}).text.strip()
                })

        data.append(data_obj)

    # crawl website for links
    visited_pages.append(page)

with open('file.json', 'w') as out_file:
    json.dump(data, out_file, ensure_ascii=False)