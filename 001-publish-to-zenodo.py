# -*- coding: utf-8 -*-
'''
* Updated on 2023/02/22
* python3
**
* 
* features:
* - upload processed data on Zenodo
'''


import os, pathlib
import configparser
import zenodopy

# load zenodo config
configfile = pathlib.Path('data/config.ini')
config = configparser.ConfigParser()
config.sections()
config.read(configfile)

assert config['zenodo']['zenodo'] == 'True'

'''
# sandbox for test
ZENODO_SANDBOX_API_TOKEN = os.environ.get('ZENODO_SANDBOX_API_TOKEN')
zenodo = zenodopy.Client(sandbox=True,token=ZENODO_SANDBOX_API_TOKEN)
'''
ZENODO_API_TOKEN = os.environ.get('ZENODO_API_TOKEN')
zenodo = zenodopy.Client(token=ZENODO_API_TOKEN)

recordid = config['zenodo']['recordid']
new_record = zenodo.get_latest_record(recordid)
zenodo.set_project(new_record)
zenodo.download_file('data.zip')
zenodo.update(pathlib.Path('data'), 'data.zip', publish=True)
