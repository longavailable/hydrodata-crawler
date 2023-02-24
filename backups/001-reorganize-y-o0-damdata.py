# -*- coding: utf-8 -*-
'''
* Updated on 2023/02/24
* python3
**
* re-organize data in https://github.com/y-o0/damdata/tree/master/jsons
'''

from datetime import datetime
print('Started at', datetime.now())

import json
import pathlib
if pathlib.Path('mytool/lots/util.py').is_file():
	from mytool.lots.util import recordExist_dict, writeLogsDicts2csv
else:
	from lots.util import recordExist_dict, writeLogsDicts2csv

stcds = ['60107000', '61802500', '60115000']

filenames = list(pathlib.Path('damdata/jsons').glob('*.json'))
for filename in filenames:
	with open(filename) as f:
		data = json.load(f)
	for i, d in enumerate(data):
		if d['stcd'] in stcds:
			time = datetime.fromtimestamp(int(d['tm'])/1000)
			ct = { 'year': time.year, 'month': time.month, 'day': time.day, 'hour': time.hour}
			record = { **ct }
			# z
			if 'z' not in d.keys() or float(d['z'])<=0: 
				print(d['stcd'], time, 'z')
				record['Z'] = ''
			else:
				record['Z'] = d['z']
			# q
			if 'q' not in d.keys() or float(d['q']) <= 0: 
				print(d['stcd'], time, 'q')
				record['Q'] = ''
			else:
				record['Q'] = d['q']
			# export 
			if record['Z'] or record['Q']:
				fout = pathlib.Path('hydrodata/hourly') / ( d['stcd'] + '-' + d['rvnm'] + '-' + d['stnm'] + '.csv' )
				if not recordExist_dict(fout, ct):
					writeLogsDicts2csv(fout, record)
				
print('Done at', datetime.now())