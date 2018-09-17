import re
import json
import os
from bs4 import BeautifulSoup

dir = 'catalogue-pages'
output_dir = 'catalogue'
files = os.listdir(dir)

for file in files:
    page = open(dir + '/' + file).read()

    soup = BeautifulSoup(page, 'html.parser')
    cr_id_regex = re.compile('[ABC]\d+(?:\.\d+)?')
    state_regex = re.compile('\((first|second) state\)')
    year_regex = re.compile('1[89]\d\d')

    for div in soup.select('table.main'):
        imgs = div.select('img')
        if len(imgs) == 0:
            continue
        img = imgs[0]
        text = div.select('td[align=left]')[0].text
        share = div.select('.addthiscontainer')[0]
        direct_link = share['addthis:url']
        database_link = div.select('.database-link')[0]['href']
        matches = re.findall(cr_id_regex, text)
        year_matches = re.findall(year_regex,text)
        year = year_matches[0]
        cr_id = matches[-1]
        state_description = state_regex.search(text)
        if state_description:
            state = state_description.group(1)
            prefix = cr_id[0]
            ids = cr_id[1:].split('.')
            if state == 'first':
                cr_id = prefix + ids[0]
            else:
                cr_id = prefix + ids[1]

        file_name = 'catalogue/' + cr_id + '.json'
        output = open(file_name, 'w')
        output.write(json.dumps({
            'id': cr_id,
            'database': database_link,
            'link': direct_link,
            'thumbnail': img['src'],
            'year': year,
            'description': text,
        }, indent=2))
        output.close()
        print('Written ' + file_name)
