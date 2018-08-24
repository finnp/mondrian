"""
    Downloads images from RKD listed in the catalogue
"""

import os
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve

dir = 'catalogue'
files = os.listdir(dir)

for file in files:
    with open(dir + '/' + file) as f:
        data = json.load(f)
        page = urlopen(data['database'])
        id = data['id']
        soup = BeautifulSoup(page, 'html.parser')
        thumb_id = soup.select('.record-metadata')[0]['data-thumb-id']
        download_url = 'https://images.rkd.nl/rkd/thumb/1000x1000/' + thumb_id + '.jpg'
        urlretrieve(download_url, 'catalogue-images/' + id + '.jpg')
        print('File ' + file + ' downloaded.')
