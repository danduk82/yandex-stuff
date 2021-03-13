#!/bin/env python3

import os
import requests
import numpy as np

url_fmt = "{base}/{z}/{x}/{y}.png"
nb_urls = 100000
base_url = '/tiles/1.0.0/cesiumstreetswebmercator/default/webmerc_quad'

server='http://map.54.166.35.111.nip.io'



europe = {8: [(128,87),(136,92)]}
east_china = {8: [(202,99),(211,109)]}
conus = {8: [(44,93),(69,105)]}
countries = [europe, east_china, conus]

max_zl = 16
#for max_zl in range(8, 24):
print(max_zl)
# CONUS coverage (more or less)

for a in countries:
    for i in range(9, max_zl+1):
        c = a[i - 1]
        a[i] = [(x * 2, y * 2) for x, y in a[i - 1]]

# probabilites, should be almost the same for each country
mSizes = {k: ((v[0][1] - v[0][0] + 1) * (v[1][0] - v[0][0]) + 1) for k, v in a.items()}


p=np.array([v for x,v in mSizes.items()])
p = p / sum(p)
zl = np.random.choice(np.arange(8, max_zl+1),size=(nb_urls), p=p)

urls = []

for z in zl:
    c = np.random.randint(0,3)
    y = np.random.randint(countries[c][z][0][0], countries[c][z][1][0])
    x = np.random.randint(countries[c][z][0][1], countries[c][z][1][1])
    urls.append(url_fmt.format(**{'base':base_url ,'z':z,'y':y,'x':x}))

with open(f"{os.getenv('HOME')}/test/yandex_stuff/ammo_zl_8_{max_zl}.txt", 'w') as f:
    f.write('\n'.join(np.unique(urls)))
# c = 0
# for url in urls[0:100]:
#     r = requests.get(url)
#     if r.status_code == 200:
#         with open(f'/tmp/samere/image_{c}.png','wb') as f:
#             f.write(r.content)
    #     c+=1
