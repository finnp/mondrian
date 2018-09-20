from files import read_data

with open('paintings.txt') as f:
    for cnt, line in enumerate(f):
        data = read_data('catalogue/' + line[:-1] + '.json')
        print(data['state'])
