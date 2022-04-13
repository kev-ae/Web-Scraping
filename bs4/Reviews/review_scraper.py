from logging.handlers import DEFAULT_SOAP_LOGGING_PORT
import requests
import re
import json
from bs4 import BeautifulSoup

'''
What words are being use to describe new releases and are there any correlation between games have have a positive review and those
that have a negative review
'''

seed = 'https://store.steampowered.com/explore/new/'
api = 'https://store.steampowered.com/appreviews/{}?cursor=*&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=english&l=english&review_type=all&purchase_type=all&playtime_filter_min=0&playtime_filter_max=0&filter_offtopic_activity=1'

data = []

new_html = requests.get(seed).content
soup = BeautifulSoup(new_html, 'html.parser')
new_releases = soup.find_all('a', {'data-ds-itemkey' : re.compile('^App_[0-9]*$')})
pages_to_visit = [store_page['href'] for store_page in new_releases]


# main loop
while len(pages_to_visit) != 0:
    url = pages_to_visit.pop(0)

    search = re.search('/app/', str(url))
    if search:
        data_obj = {}
        
        # if url is a game page, get the game id
        temp = str(url)[search.end():]
        delimiter = temp.find('/')
        data_obj['game_id'] = temp[:delimiter]

        # get the title of the game
        temp = temp[delimiter + 1:]
        delimiter = temp.find('/')
        data_obj['game_title'] = temp[:delimiter]

        raw_html = requests.get(url).content
        soup = BeautifulSoup(raw_html, 'html.parser')

        # get the overall score in the last 30 days
        review_summary = soup.find('div', {'id' : 'userReviews'})
        score = review_summary.find('span', {'class' : 'responsive_reviewdesc'})
        data_obj['overall_score'] = score.text.strip() if score != None else None

        # get the best score recieve
        best = review_summary.find('meta', {'itemprop' : 'bestRating'})
        data_obj['best_score'] = best['content'] if best != None else None

        # get the worst score recieve
        worst = review_summary.find('meta', {'itemprop' : 'worstRating'})
        data_obj['worst_score'] = worst['content'] if worst != None else None

        # get the tags
        tags_container = soup.find('div', {'data-appid' : data_obj['game_id']})
        tags = tags_container.find_all('a', {'class' : re.compile('^app_tag$')})
        data_obj['tags'] = [tag.text.strip() for tag in tags if tag != None]

        # get the reviews
        data_obj['reviews'] = []
        reviews_html = requests.get(api.format(data_obj['game_id'])).json()['html']
        soup = BeautifulSoup(reviews_html, 'html.parser')
        reviews = soup.find_all('div', {'id': re.compile('^ReviewContentsummary[0-9]*$')})

        # extract data from every review
        for review in reviews:
            name_container = review.find('div', {'class' : 'persona_name'})
            data_obj['reviews'].append({
                'username' : name_container.find('a').text.strip(),
                'comment' : review.find('div', {'class' : 'content'}).text.strip() # get positive or negative
                })

        data.append(data_obj)

with open('file.json', 'w') as out_file:
    json.dump(data, out_file, ensure_ascii=False)