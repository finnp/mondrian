import os

dir = 'catalogue'
files = os.listdir(dir)

existing = []
known_missing = ['A316', 'B83']

for file in files:
    number = file.split('.')[0]
    existing.append(number)

# A check
for a in range(1,711):
    id = 'A' + str(a)
    if not id in existing and not id in known_missing:
        print(id)

for b in range(1, 416):
    id = 'B' + str(b)
    if not id in existing and not id in known_missing:
        print(id)
