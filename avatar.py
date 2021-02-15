import argparse
import configparser
import csv
import pathlib
import requests

parser = argparse.ArgumentParser(description='Add ArchivesSpace <dsc> elements from data output from the A/V Database.')
parser.add_argument('project_csv', metavar='/path/to/project/csv.csv', type=pathlib.Path, help='Path to a project CSV')
parser.add_argument('-d', '--dst', metavar='/path/to/destination/directory', type=pathlib.Path, help='Path to destination directory for results')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.ini')
base_url = config['ArchivesSpace']['BaseURL']
user = config['ArchivesSpace']['User']
password = config['ArchivesSpace']['Password']

print('authenticating to ArchivesSpace')
endpoint = '/users/' + user + '/login'
params = {'password': password}
response = requests.post(base_url + endpoint, params=params)
print(response.text)

response = response.json()
session_key = response['session']

print('parsing project CSV')
collections = []
items = []
parts = []

results = []
print(args.dest)
with open(args.project_csv, encoding='utf-8') as f:
    reader = csv.DictReader(f)
