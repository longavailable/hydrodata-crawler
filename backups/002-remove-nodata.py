# -*- coding: utf-8 -*-
'''
* Updated on 2023/02/24
* python3
**
* remove nodata lines
'''

from datetime import datetime
print('Started at', datetime.now())

import pathlib
import pandas as pd

filenames = list(pathlib.Path('data/hourly').glob('*.csv'))

for filename in filenames:
	data = pd.read_csv(filename, low_memory=False)
	data2 = data.dropna(subset=['Z', 'Q'], how='all').sort_values(by=['year', 'month', 'day', 'hour'])
	data2.to_csv(filename, index=False)

print('Done at', datetime.now())