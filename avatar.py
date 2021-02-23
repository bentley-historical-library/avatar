import argparse
import configparser
import csv
import json
import os
import pathlib
import requests

parser = argparse.ArgumentParser(description='Add ArchivesSpace <dsc> elements from data output from the A/V Database.')
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
        
        audio_or_moving_image = ''
        if 'SR' in row['DigFile Calc'].strip():
            audio_or_moving_image = 'audio'
        else:
            audio_or_moving_image = 'moving image'

        digfile_calc = row['DigFile Calc'].strip()
        type_of_digfile_calc = ''
        if audio_or_moving_image == 'audio' and len(digfile_calc.split('-')) > 3:
            type_of_digfile_calc = 'item with parts'
        elif audio_or_moving_image == 'audio' in digfile_calc and len(digfile_calc.split('-')) == 3:
            type_of_digfile_calc = 'item ONLY'
        if audio_or_moving_image == 'moving image' and len(digfile_calc.split('-')) > 2:
            type_of_digfile_calc - 'item with parts'
        elif audio_or_moving_image == 'moving image' and len(digfile_calc.split('-')) == 2:
            type_of_digfile_calc = 'item ONLY'

        # parse the rest of the csv
        extent_type = row['AVType::ExtentType']
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
            item = {
                'archival_object_id': archival_object_id,
                'type_of_archival_object_id': type_of_archival_object_id,
                'digfile_calc': digfile_calc,
                'type_of_digfile_calc': type_of_digfile_calc,
                'audio_or_moving_image': audio_or_moving_image,
                'extent_type': extent_type,
                'av_type': av_type,
                'item_title': item_title,
                'item_part_title': item_part_title,
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
            
            digfile_calc_item = '-'.join(digfile_calc.split('-')[0:-1])
            item = {
                'archival_object_id': archival_object_id,
                'type_of_archival_object_id': type_of_archival_object_id,
                'digfile_calc_item': digfile_calc_item,
                'type_of_digfile_calc': type_of_digfile_calc,
                'audio_or_moving_image': audio_or_moving_image,
                'extent_type': extent_type,
                'av_type': av_type,
                'item_title': item_title,
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
            parts.append(part)

print("Alright, we're done!")
