from bs4 import BeautifulSoup
from urllib.request import urlopen

url_seed = 'https://store.steampowered.com/'

connection = urlopen(url_seed)
raw_html = connection.read()
connection.close()

soup = BeautifulSoup(raw_html, 'html.parser')
games = soup.findAll('a', {'class':'tab_item'})

output_file = 'steam.csv'
fd = open(output_file, 'w')
fd.write('Title,Price,Tags\n')

for game in games:
    price = game.find('div', {'class':'discount_final_price'})
    if price != None:
        price = price.text

    title_container = game.find('div', {'class':'tab_item_content'})
    title = title_container.find('div', {'class':'tab_item_name'}).text

    tags = title_container.find('div', {'tab_item_details'}).text.strip().replace(',', ' |')

    fd.write('{},{},{}\n'.format(title, price, tags))

fd.close()