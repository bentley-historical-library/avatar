import argparse
import configparser
import csv
import json
import os
import pathlib
import requests

from avatar.parent_and_item_only import parent_and_item_only
from avatar.item_and_item_only import item_and_item_only
from avatar.parent_and_item_with_parts import parent_and_item_with_parts
from avatar.item_and_item_with_parts import item_and_item_with_parts
from avatar.part_and_item_with_parts import part_and_item_with_parts

parser = argparse.ArgumentParser(description='Creates or updates ArchivesSpace `<dsc>` archival and digital object elements using data output from the A/V Database')
parser.add_argument('project_csv', metavar='/path/to/project/csv.csv', type=pathlib.Path, help='Path to a project CSV')
parser.add_argument('-o', '--output', metavar='/path/to/output/directory', type=pathlib.Path, help='Path to output directory for results')
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
    
        # characterize each row in the spreadsheet
        archival_object_id = row['object id'].strip()
        type_of_archival_object_id = row['Type of obj id'].strip()
        if not type_of_archival_object_id:
            print('skipping ' + row['DigFile Calc'])
            continue
            
        print(row['DigFile Calc'] + ' is a: ' + type_of_archival_object_id)
        
        audio_or_moving_image = ''
        if 'SR' in row['DigFile Calc'].strip():
            audio_or_moving_image = 'audio'
        else:
            audio_or_moving_image = 'moving image'
        print(row['DigFile Calc'] + ' is a: ' + audio_or_moving_image)

        digfile_calc = row['DigFile Calc'].strip()
        coll_item_number = row['CollItem No'].strip()
        type_of_digfile_calc = ''
        if digfile_calc == coll_item_number:
            type_of_digfile_calc = 'item ONLY'
        elif digfile_calc != coll_item_number:
            type_of_digfile_calc = 'item with parts'
        print(row['DigFile Calc'] + ' is a: ' + type_of_digfile_calc)

        # parse the rest of the csv
        resource_id = row['resource id']
        extent_type = row['AVType::ExtentType'].lower()
        av_type = row['AVType::Avtype']
        item_title = row['ItemTitle']
        item_part_title = row['ItemPartTitle']
        item_date = row['ItemDate']
        mivideo_id = row['MiVideoID']
        note_content = row['NoteContent']
        note_technical = row['NoteTechnical']
        fidelity = row['AUDIO_ITEMCHAR::Fidleity']
        reel_size = row['AUDIO_ITEMCHAR::ReelSize']
        tape_speed = row['AUDIO_ITEMCHAR::TapeSpeed']
        item_source_length = row['AUDIO_ITEMCHAR::ItemSourceLength']
        item_polarity = row['ItemPolarity']
        item_color = row['ItemColor']
        item_sound = row['ItemSound']
        item_length = row['ItemLength']
        item_time = row['ItemTime']
        
        # build the items and, optionally, parts
        if type_of_digfile_calc == 'item ONLY':
            
            digfile_calc_item = coll_item_number
            item = {
                'resource_id': resource_id,
                'archival_object_id': archival_object_id,
                'type_of_archival_object_id': type_of_archival_object_id,
                'digfile_calc': digfile_calc,
                'digfile_calc_item': digfile_calc_item,
                'type_of_digfile_calc': type_of_digfile_calc,
                'audio_or_moving_image': audio_or_moving_image,
                'extent_type': extent_type,
                'av_type': av_type,
                'item_title': item_title,
                'item_part_title': item_part_title, # just in case
                'item_date': item_date,
                'mivideo_id': mivideo_id,
                'note_content': note_content,
                'note_technical': note_technical,
                'fidelity': fidelity,
                'reel_size': reel_size,
                'tape_speed': tape_speed,
                'item_source_length': item_source_length,
                'item_polarity': item_polarity,
                'item_color': item_color,
                'item_sound': item_sound,
                'item_length': item_length,
                'item_time': item_time
            }
            items.append(item)
            
        elif type_of_digfile_calc == 'item with parts':
            
            digfile_calc_item = coll_item_number
            item = {
                'resource_id': resource_id,
                'archival_object_id': archival_object_id,
                'type_of_archival_object_id': type_of_archival_object_id,
                'digfile_calc': digfile_calc,
                'digfile_calc_item': digfile_calc_item,
                'type_of_digfile_calc': type_of_digfile_calc,
                'audio_or_moving_image': audio_or_moving_image,
                'extent_type': extent_type,
                'av_type': av_type,
                'item_title': item_title,
                'reel_size': reel_size,
                'fidelity': fidelity,
                'tape_speed': tape_speed,
                'item_source_length': item_source_length,
                'item_polarity': item_polarity,
                'item_color': item_color,
                'item_sound': item_sound,
                'item_length': item_length,
            }
            items.append(item)
            
            digfile_calc_part = digfile_calc
            part = {
                'archival_object_id': archival_object_id,
                'type_of_archival_object_id': type_of_archival_object_id,
                'digfile_calc_item': digfile_calc_item,
                'digfile_calc_part': digfile_calc_part,
                'type_of_digfile_calc': type_of_digfile_calc,
                'audio_or_moving_image': audio_or_moving_image,
                'item_part_title': item_part_title,
                'item_date': item_date,
                'mivideo_id': mivideo_id,
                'note_content': note_content,
                'note_technical': note_technical,
                'item_time': item_time
            }
            parts.append(part)

for item in items:
    print('\nadding archivesspace <dsc> elements from data output from the a/v database for ' + item['digfile_calc'])
    
    if item['type_of_archival_object_id'] == 'Parent' and item['type_of_digfile_calc'] == 'item ONLY':
        
        print('\nthe corresponding archivesspace archival object is a parent and the row is an item only')
        archival_object_id = parent_and_item_only(repository_id, base_url, session_key, item)
        results.append([item['digfile_calc'], archival_object_id])
        
    elif item['type_of_archival_object_id'] == 'Item' and item['type_of_digfile_calc'] == 'item ONLY':
        print('the corresponding archivesspace archival object is an item and the row is an item only')
        item_and_item_only(repository_id, base_url, session_key, item)
        # results.append([item['dig]])
    
    elif item['type_of_archival_object_id'] == 'Parent' and item['type_of_digfile_calc'] == 'item with parts':
        print('the corresponding archivesspace archival object is a parent and the row is an item with parts')
        archival_object_id = parent_and_item_with_parts(repository_id, base_url, session_key, item, parts)
        results.append([item['digfile_calc'], archival_object_id])
    
    elif item['type_of_archival_object_id'] == 'Item' and item['type_of_digfile_calc'] == 'item with parts':
        print('the corresponding archivesspace archival object is an item and the row is an item with parts')
        item_and_item_with_parts(repository_id, session_key, item, parts)
    
    elif item['type_of_archival_object_id'] == 'Part' and item['type_of_digfile_calc'] == 'item with parts':
        print('the corresponding archivesspace archival object is a part and the row is an item with parts')
        archival_object_id = part_and_item_with_parts(repository_id, base_url, session_key, item, parts)
        results.append([item['digfile_calc'], archival_object_id])

print("Alright, we're done!")
