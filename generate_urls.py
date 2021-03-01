#!/bin/env python3

import requests
import numpy as np

url_fmt = "{base}/{z}/{x}/{y}.png"
nb_urls = 50000
base_url = '/tiles/1.0.0/cesiumstreetswebmercator/default/webmerc_quad'

server='http://map.54.166.35.111.nip.io'

for max_zl in range(8, 24):
    print(max_zl)
    # CONUS coverage (more or less)
    a = {
        2: [(0, 0), (1, 1)],
        3: [(1, 2), (2, 3)],
        4: [(2, 4), (4, 6)],
        5: [(5, 11), (9, 12)],
    }
    for i in range(6, max_zl+1):
        c = a[i - 1]
        a[i] = [(x * 2, y * 2) for x, y in a[i - 1]]
    
    
    mSizes = {k: ((v[0][1] - v[0][0] + 1) * (v[1][0] - v[0][0]) + 1) for k, v in a.items()}
    
    
    p=np.array([v for x,v in mSizes.items()])
    p = p / sum(p)
    zl = np.random.choice(np.arange(2, max_zl+1),size=(nb_urls), p=p)
    
    urls = []
    for z in zl:
        y = np.random.randint(a[z][0][0], a[z][1][0])
        x = np.random.randint(a[z][0][1], a[z][1][1])
        urls.append(url_fmt.format(**{'base':base_url ,'z':z,'y':y,'x':x}))
    
    with open(f'ammo_zl_0_{max_zl}.txt', 'w') as f:
        f.write('\n'.join(urls))
    # c = 0
    # for url in urls[0:100]:
    #     r = requests.get(url)
    #     if r.status_code == 200:
    #         with open(f'/tmp/samere/image_{c}.png','wb') as f:
    #             f.write(r.content)
    #     c+=1
