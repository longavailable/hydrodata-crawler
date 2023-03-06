# -*- coding: utf-8 -*-
'''
* Updated on 2023/03/06
* python3
**
* Calculate daily average for water levels / flows
'''

from datetime import datetime
print('Started at', datetime.now())

import pathlib
import pandas as pd
from twaw import dailyAverage

filenames = list(pathlib.Path('data/hourly').glob('*.csv'))
for filename in filenames:
	data = pd.read_csv(filename)
	data['time'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])

	items = ['Z', 'Q']
	results = dailyAverage(data, itemHeader=items, timeHeader='time')

	newdata = pd.DataFrame(data=results)
	newdata2 = newdata.dropna(subset=items, how='all').sort_values(by=['year', 'month', 'day'])
	if len(newdata2) > 0:
		filename2 = filename.parents[1] / 'daily' / filename.name
		filename2.mkdir(parents=True, exist_ok=True)
		newdata2.to_csv(filename2, index=False)
	else:
		print('No data to export!')
	
print('Done at', datetime.now())