import argparse
import configparser
import csv
import json
import os
import pathlib
import requests

parser = argparse.ArgumentParser(description='Add ArchivesSpace <dsc> elements from data output from the A/V Database.')
parser.add_argument('project_csv', metavar='/path/to/project/csv.csv', type=pathlib.Path, help='Path to a project CSV')
parser.add_argument('-d', '--dst', metavar='/path/to/destination/directory', type=pathlib.Path, help='Path to destination directory for results')
args = parser.parse_args()

print('parsing config.ini')
config = configparser.ConfigParser()
config.read('config.ini')
base_url = config['ArchivesSpace']['BaseURL']
user = config['ArchivesSpace']['User']
password = config['ArchivesSpace']['Password']
repository_id = config['ArchivesSpace']['RepositoryID']

print('authenticating to ArchivesSpace')
endpoint = '/users/' + user + '/login'
params = {'password': password}
response = requests.post(base_url + endpoint, params=params)
print(response.text)

response = response.json()
session_key = response['session']

print('parsing project CSV')
items = []
parts = []

results = []

with open(args.project_csv, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
    
        digfile_calc = row['DigFile Calc'].strip()
        type_of_object_id = row['Type of obj id'].strip()
                
        if not type_of_object_id:
            print('skipping ' + digfile_calc)
            continue
            
        elif type_of_object_id == 'Item':
            archival_object_id = row['object id'].strip()
            
            print('GETting archival object ' + str(archival_object_id))
            endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
            headers = {'X-ArchivesSpace-Session': session_key}
            response = requests.get(base_url + endpoint, headers=headers)
            print(response.text)
            
            item = response.json()
            
            '''
            UPDATE Archival Object'''
            # basic information
            item_title = row['ItemTitle'].strip()
            item_part_title = row['ItemPartTitle'].strip()
            title = item_title
            if item_part_title:
                title = title + ' ' + item_part_title
            
            item['title'] = title
            item['component_id'] = digfile_calc
            item['level'] = 'file'
            
            # dates
            item_date = row['ItemDate'].strip()
            
            item['dates'] = [
                {
                    'label': 'creation',
                    'expression': item_date,
                    'date_type': 'inclusive'
                }
            ]
            
            # extents
            extent_type = row['AVType::ExtentType'].strip().lower()
            # physical details
            av_type = row['AVType::Avtype'].strip()
            physical_details = av_type
            # audio
            audio_physical_details = []
            reel_size = row['AUDIO_ITEMCHAR::ReelSize'].strip()
            if reel_size:
                audio_physical_details.append(reel_size)
            tape_speed = row['AUDIO_ITEMCHAR::TapeSpeed'].strip()
            if tape_speed:
                audio_physical_details.append(tape_speed)
            fidelity = row['AUDIO_ITEMCHAR::Fidleity'].strip()
            if fidelity:
                audio_physical_details.append(fidelity)
            audio_extent_types = config['ExtentTypes']['Audio'].split(', ')
            if audio_physical_details and extent_type in audio_extent_types:
                physical_details = physical_details + '; ' + '; '.join(audio_physical_details)
            # video
            video_physical_details = []
            item_polarity = row['ItemPolarity'].strip()
            if item_polarity:
                video_physical_details.append(item_polarity)
            item_color = row['ItemColor'].strip()
            if item_color:
                video_physical_details.append(item_color)
            item_sound = row['ItemSound'].strip()
            if item_sound:
                video_physical_details.append(item_sound)
            video_extent_types = config['ExtentTypes']['Video'].split(', ')
            if video_physical_details and extent_type in video_extent_types:
                physical_details = physical_details + '; ' + '; '.join(video_physical_details)
            item_time = row['ItemTime'].strip()
            
            item['extents'] = [
                {
                    'portion': 'whole',
                    'number': '1',
                    'extent_type': extent_type,
                    'physical_details': physical_details,
                    'dimensions': item_time
                }
            ]
           
            # notes
            # abstract
            note_content = row['NoteContent'].strip()
            abstracts = [note for note in item['notes'] if note['type'] == 'abstract']
            
            if abstracts:
                for abstract in abstracts:
                    abstract['content'] = [note_content]
            else:
                item['notes'].append(
                    {
                        'jsonmodel_type': 'note_singlepart',
                        'type': 'abstract',
                        'content': [note_content]
                    }
                )
            # conditions governing access
            # #coming soon
            
            print(json.dumps(item))
            print('POSTing archival object ' + str(archival_object_id))
            response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(item))
            print(response.text)
    
            results.append([digfile_calc, archival_object_id])
            
            '''
            CREATE Digital Object (Preservation)'''
            print('GETting archival object ' + str(archival_object_id))
            endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
            response = requests.get(base_url + endpoint, headers=headers)
            print(response.text)
            
            archival_object = response.json()
            display_string = archival_object['display_string']
            
            collection_id = digfile_calc.split('-')[0]
            item_id = collection_id
            if extent_type in audio_extent_types:
                item_id = item_id + '-SR-' + digfile_calc.split('-')[2]
            elif extent_type in video_extent_types:
                item_id = item_id + '-' + digfile_calc.split('-')[1]
            
            # basic information
            digital_object_preservation = {
                'jsonmodel_type': 'digital_object',
                'title': display_string,
                'digital_object_id': item_id,
                'publish': False,
                'file_versions': [],
                'repository': {
                    'ref': '/repositories/' + str(repository_id)
                }
            }
            # file versions
            if extent_type in audio_extent_types:
                digital_object_preservation['file_versions'] = [
                    {
                        'jsonmodel_type': 'file_version',
                        'file_uri': os.path.join('R:', os.sep, 'AV Collections', 'Audio', collection_id, item_id),
                        'publish': False                    
                    }
                ]
            elif extent_type in video_extent_types:
                digital_object_preservation['file_versions'] = [
                    {
                        'jsonmodel_type': 'file_version',
                        'file_uri': os.path.join('R:', os.sep, 'AV Collections', 'Moving Image', collection_id, item_id),
                        'publish': False
                    }
                ]
            
            print(json.dumps(digital_object_preservation))
            print('POSTing digital object (preservation) for ' + item_id)
            endpoint = '/repositories/' + str(repository_id) + '/digital_objects'
            response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(digital_object_preservation))
            print(response.text)
            
            # Note: This will sometimes throw an error ({"error":{"digital_object_id":["Must be unique"]}}) when the "Item" (Type of obj id) is actually a part. But you still get to the same result.
