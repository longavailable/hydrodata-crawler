# -*- coding: utf-8 -*-
'''
* Updated on 2023/02/10
* python3
**
* crawl / download hydrological data (water level and flow)
* features:
* - data source: 'http://113.57.190.228:8001/web/Report/RiverReport' (湖北水利厅|办事服务|江河水情),
* - access the webpage by requests,
* - parse data / conten with lxml, 
* - export in csv format.
'''

from datetime import datetime, date, timedelta
print('Started at', datetime.now())

import requests
import pathlib, time, re, random
import configparser
from lots.util import recordExist_dict, writeLogsDicts2csv, writeLogs, is_number

items = ['STCD', 'RVNM', 'STNM', 'Z', 'Q']
stios = ['三峡水库', '丹江口水库', '水布垭', '隔河岩']	# The stations have inflow and outflow.

headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
								'Chrome/85.0.4183.83 YaBrowser/20.9.0.933 Yowser/2.5 Safari/537.3 ',
	}

url = 'http://113.57.190.228:8001/web/Report/GetRiverData'

s = requests.Session()
s.headers = headers

# load initial time
configfile = pathlib.Path('data/config.ini')
config = configparser.ConfigParser()
config.sections()
config.read(configfile)
time0 = datetime( 	int(config['hbsl']['year']),
					int(config['hbsl']['month']),
					int(config['hbsl']['day']),
					int(config['hbsl']['hour']))
# end date
time1 = datetime( date.today().year, date.today().month, date.today().day, 0)
print('t0:', time0, 't1:', time1)

# main part
while time0 < time1:
	
	# current time
	ct = { 'year': time0.year, 'month': time0.month, 'day': time0.day, 'hour': time0.hour}
	# request parameters
	payload = {'date': time0.strftime('%Y-%m-%d %H:00')}
	page = s.get(url, params=payload)
	if page.ok:
		for i, d in enumerate(page.json()['rows']):
			# left panel
			if items[0] in d:
				'''
				# rename legacy files
				filename1 = pathlib.Path('data/hourly') / ( d['STNM'] + '.txt')
				if filename1.is_file():
					filename2 = filename1.parent / ( d['STCD'] + '-' + d['RVNM'] + '-' + d['STNM'] + '.csv' )
					filename1.rename(filename2)
				'''
				
				record = { **ct, 'Z': d['Z'] }
				# Q for reservoirs
				if d['STNM'] in stios:
					# inflow of reservoir
					if '入' in d['Q'] or is_number(d['Q']): 
						record['Q'] = re.findall(r'[-+]?(?:\d*\.*\d+)', d['Q'])[0]
					else:
						record['Q'] = ''
					filename = pathlib.Path('data/hourly') / ( d['STCD'] + '-' + d['RVNM'] + '-' + d['STNM'] + '入.csv' )
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
						
					# outflow of reservoir
					if '出' in d['Q']: 
						record['Q'] = re.findall(r'[-+]?(?:\d*\.*\d+)', d['Q'])[-1]
					else:
						record['Q'] = ''
					filename = pathlib.Path('data/hourly') / ( d['STCD'] + '-' + d['RVNM'] + '-' + d['STNM'] + '出.csv' )
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
						
				# Q for general stations
				else:
					record['Q'] = d['Q']
					filename = pathlib.Path('data/hourly') / ( d['STCD'] + '-' + d['RVNM'] + '-' + d['STNM'] + '.csv' )
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
			# right panel
			if items[0] + '1' in d:
				'''
				# rename legacy files
				filename1 = pathlib.Path('data/hourly') / ( d['STNM1'] + '.txt')
				if filename1.is_file():
					filename2 = filename1.parent / ( d['STCD1'] + '-' + d['RVNM1'] + '-' + d['STNM1'] + '.csv' )
					filename1.rename(filename2)
				'''
				record = { **ct, 'Z': d['Z1'] }
				if d['STNM1'] in stios:
					if '入' in d['Q1'] or is_number(d['Q1']): 
						record['Q'] = re.findall(r'[-+]?(?:\d*\.*\d+)', d['Q1'])[0]
					else:
						record['Q'] = ''
					filename = pathlib.Path('data/hourly') / ( d['STCD1'] + '-' + d['RVNM1'] + '-' + d['STNM1'] + '入.csv' )
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
						
					if '出' in d['Q1']: 
						record['Q'] = re.findall(r'[-+]?(?:\d*\.*\d+)', d['Q1'])[-1]
					else:
						record['Q'] = ''
					filename = pathlib.Path('data/hourly') / ( d['STCD1'] + '-' + d['RVNM1'] + '-' + d['STNM1'] + '出.csv' )
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
					
				else:
					record['Q'] = d['Q1']
					filename = pathlib.Path('data/hourly') / ( d['STCD1'] + '-' + d['RVNM1'] + '-' + d['STNM1'] + '.csv' )
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
	else:
		print('Task was interrupted at', time0)
		break
	
	# next hour
	time0 = time0 + timedelta(hours=1)
	time.sleep(random.randint(2, 6))

# reset configfile
lt = { 'year': time0.year, 'month': time0.month, 'day': time0.day, 'hour': time0.hour}
config['hbsl'] = lt
with open(configfile, 'w') as f:
	config.write(f)

print('Done at', datetime.now())