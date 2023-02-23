# -*- coding: utf-8 -*-
'''
* Updated on 2023/02/23
* python3
**
* remove nodata lines
'''

from datetime import datetime, date, timedelta
print('Started at', datetime.now())

import pathlib
import configparser

if pathlib.Path('mytool/lots/util.py').is_file():
	from mytool.lots.util import daterange, removeLogs
else:
	from lots.util import daterange, removeLogs

date0 = date(2000, 1, 1)
date1 = date.today()
dates = daterange(date0, date1)

hour0, hour1 = 0, 23
hours = list(range(hour0, hour1+1))

nodata = ['%d,%d,%d,%d,,' % (d.year, d.month, d.day, h) for d in dates for h in hours]

filenames = list(pathlib.Path('data/hourly').glob('*.csv'))

for filename in filenames:
	removeLogs(filename, nodata, headers=True)

print('Done at', datetime.now())