# -*- coding: utf-8 -*-
'''
* Updated on 2023/02/23
* python3
**
* crawl / download hydrological data (water level and flow)
* features:
* - data source: 'http://yc.wswj.net/ahsxx/LOL/?refer=upl&to=public_public' (安徽水利厅|安徽水信息|水情专题),
* - access the webpage by requests,
* - export in csv format.
'''

from datetime import datetime, date, timedelta
print('Started at', datetime.now())

import requests
import js2py
import pathlib, time, random, json
import configparser
from lots.util import recordExist_dict, writeLogsDicts2csv


headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
								'Chrome/85.0.4183.83 YaBrowser/20.9.0.933 Yowser/2.5 Safari/537.3 ',
	}

url = 'http://61.191.22.196:5566/AHSXX/service/PublicBusinessHandler.ashx'

s = requests.Session()
s.headers = headers

# encode/decode functions
js_link = [ 'http://yc.wswj.net/ahsxx/lol/script/watersecurity.js',
	'https://raw.githubusercontent.com/longavailable/datarepo02/main/code/javascript/waterSecurity.js'	]

try:
	waterSecurity = js2py.eval_js(s.get(js_link[0]).text)
except:
	waterSecurity = js2py.eval_js(s.get(js_link[1]).text)

'''
# test
print(waterSecurity.encode('60115000'))	#stcd: 2.1MDYxMTA1MDA=
print(waterSecurity.encode('202302040800'))	#btime, etime
print(waterSecurity.encode('202302141100'))
print(waterSecurity.encode('GetSwLineMap'))	#name: 2.1ZUdTdEx3bmlNZXBh
print(waterSecurity.encode('GetSwLineAndZX'))	#name: 2.1ZUdTdEx3bmlBZWRuWFo=
print(waterSecurity.encode('GetRvsect'))	#name: 2.1ZUdSdHN2Y2UqdA==
print(waterSecurity.encode('ZQ'))		#sttp: 2.1UVo=
print(waterSecurity.encode('true'))		#waterEncode: 2.1UVo=
'''

# basic payload parameters
payload = {
	'name': waterSecurity.encode('GetSwLineMap'),
	'stcd': waterSecurity.encode('60115000'),
	'btime': waterSecurity.encode('202202141100'),
	'etime': waterSecurity.encode('202202141100'),
	'sttp': waterSecurity.encode('ZQ'),
	'waterEncode': waterSecurity.encode('true')
	}

# load initial time
configfile = pathlib.Path('data/config.ini')
config = configparser.ConfigParser()
config.sections()
config.read(configfile)
time0 = datetime( 	int(config['datong']['year']),
					int(config['datong']['month']),
					int(config['datong']['day']),
					int(config['datong']['hour']))
# end date
time1 = datetime( date.today().year, date.today().month, date.today().day, 0)
print('t0:', time0, 't1:', time1)

filename = pathlib.Path('data/hourly/60115000-长江-大通.csv')

# main part
while time0 < time1:
	
	time2 = min( time0 + timedelta(days=5), time1)
	
	# update request parameters
	payload['btime'] = waterSecurity.encode(time0.strftime('%Y%m%d%H%M'))
	payload['etime'] = waterSecurity.encode(time2.strftime('%Y%m%d%H%M'))
	page = s.get(url, params=payload)
	
	if page.ok:
		# decode data
		data = json.loads(waterSecurity.decode(page.json()['data']))
		
		if data['data_sw'] or data['data_q']:
			while time0 < time2:
				
				# current time
				ct = { 'year': time0.year, 'month': time0.month, 'day': time0.day, 'hour': time0.hour}
				# z
				z = ''
				for i, k in enumerate(data['data_sw']):
					tm = datetime.strptime(data['data_sw'][i]['TM'], '%Y-%m-%d %H:%M')
					if tm == time0:
						z = data['data_sw'][i]['Z']
						break
				# q
				q = ''
				for i, k in enumerate(data['data_q']):
					tm = datetime.strptime(data['data_q'][i]['TM'], '%Y-%m-%d %H:%M')
					if tm == time0:
						q = data['data_q'][i]['Q']
						break
				
				if z or q:
					record = { **ct, 'Z': z, 'Q': q }
					if not recordExist_dict(filename, ct):
						writeLogsDicts2csv(filename, record)
				
				# next hour
				time0 = time0 + timedelta(hours=1)
		else:
			print('[NODATA]', time0, time2)
	
	else:
		print('Task was interrupted at', time0)
		break
	
	# next 5 days
	time0 = time2
	time.sleep(random.randint(2, 6))

# reset configfile
lt = { 'year': time0.year, 'month': time0.month, 'day': time0.day, 'hour': time0.hour}
config['datong'] = lt
with open(configfile, 'w') as f:
	config.write(f)

print('Done at', datetime.now())