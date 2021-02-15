import argparse
import configparser
import requests

parser = argparse.ArgumentParser(description='Add ArchivesSpace <dsc> elements from data in the A/V Database.')
parser.add_argument('project_csv', help='Path to a project CSV')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.ini')
base_url = config['ArchivesSpace']['BaseURL']
user = config['ArchivesSpace']['User']
password = config['ArchivesSpace']['Password']

print('authenticating')
endpoint = '/users/' + user + '/login'
params = {'password': password}
response = requests.post(base_url + endpoint, params=params)
print(response.text)

response = response.json()
session_key = response['session']
