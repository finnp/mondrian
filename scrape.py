from urllib.request import urlopen
import re
import json
from bs4 import BeautifulSoup

# page = urlopen('http://catalogue.pietmondrian.nl/paris-2-1920-1937-b104-b281.312/1920-1921-b104-b132')

page = open('input.html').read()

output_dir = 'catalogue'

soup = BeautifulSoup(page, 'html.parser')
cr_id_regex = re.compile('B\d+')

for div in soup.select('table.main'):
    img = div.select('img')[0]
    text = div.select('td[align=left]')[0].text
    cr_id = cr_id_regex.search(text).group(0)

    file_name = 'catalogue/' + cr_id + '.json'
    output = open(file_name, 'w')
    output.write(json.dumps({
        'id': cr_id,
        'thumbnail': img['src'],
        'description': text
    }, indent=2))
    output.close()
    print('Written ' + file_name)
