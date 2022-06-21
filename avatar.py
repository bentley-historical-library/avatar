import argparse
from collections import Counter
import configparser
import csv
import json
import os
import pathlib
import pickle
import requests

from avatar.coll_info import coll_info
from avatar.parent_and_item_only import parent_and_item_only
from avatar.item_and_item_only import item_and_item_only
from avatar.parent_and_item_with_parts import parent_and_item_with_parts
from avatar.item_and_item_with_parts import item_and_item_with_parts
from avatar.part_and_item_with_parts import part_and_item_with_parts

parser = argparse.ArgumentParser(description='Creates or updates ArchivesSpace `<dsc>` archival and digital object elements using data output from the A/V Database')
parser.add_argument('project_csv', metavar='/path/to/project/csv.csv', type=pathlib.Path, help='Path to a project CSV')
parser.add_argument('config_choices', choices=['dev', 'prod', 'sandbox'], help='Choose configuration for DEV, PROD, or SANDBOX ArchivesSpace instance')
parser.add_argument('-c', '--coll_info', action='store_true', help='Updates collection-level-information')
parser.add_argument('-d', '--dsc', action='store_true', help='Updates container list')
parser.add_argument('-o', '--output', metavar='/path/to/output/directory', type=pathlib.Path, help='Path to output directory for results')
args = parser.parse_args()

print('parsing config.ini')
config = configparser.ConfigParser()
config.read('config.ini')

base_url = ''
user = ''
password = ''
repository_id = 2 # default archivesspace repository id

if args.config_choices == 'dev':
    base_url = config['DEV']['BaseURL']
    user = config['DEV']['User']
    password = config['DEV']['Password']
    repository_id = config['DEV']['RepositoryID']
elif args.config_choices == 'prod':
    base_url = config['PROD']['BaseURL']
    user = config['PROD']['User']
    password = config['PROD']['Password']
    repository_id = config['PROD']['RepositoryID']
elif args.config_choices == 'sandbox':
    base_url = config['SANDBOX']['BaseURL']
    user = config['SANDBOX']['User']
    password = config['SANDBOX']['Password']
    repository_id = config['SANDBOX']['RepositoryID']
    
print('authenticating to ArchivesSpace')
endpoint = '/users/' + user + '/login'
params = {'password': password}
response = requests.post(base_url + endpoint, params=params)
print(response)

response = response.json()
session_key = response['session']

if args.coll_info == True:
    print('parsing project CSV to update collection-level information')
    
    resource_ids = []
    resource_ids_to_audio_or_moving_image = []
    resource_ids_to_number_audio_and_number_moving_image = []
    with open(args.project_csv, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            resource_id = row['resource id']
            resource_ids.append(resource_id)            
            
            if resource_id not in [resource_id_to_audio_or_moving_image['resource_id'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image]:
                resource_ids_to_audio_or_moving_image.append({
                    'resource_id': resource_id,
                    'audio': False,
                    'moving_image': False
                })
            
            resource_id_to_update = [resource_id_to_audio_or_moving_image for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == resource_id][0]
            if 'SR' in row['DigFile Calc'].strip():
                resource_id_to_update['audio'] = True
            else:
                resource_id_to_update['moving_image'] = True
                
            if resource_id not in [resource_id_to_number_audio_and_number_moving_image['resource_id'] for resource_id_to_number_audio_and_number_moving_image in resource_ids_to_number_audio_and_number_moving_image]:
                resource_ids_to_number_audio_and_number_moving_image.append({
                    'resource_id': resource_id,
                    'audio': 0,
                    'moving_image': 0
                })
            
            resource_id_to_update = [resource_id_to_number_audio_and_number_moving_image for resource_id_to_number_audio_and_number_moving_image in resource_ids_to_number_audio_and_number_moving_image if resource_id_to_number_audio_and_number_moving_image['resource_id'] == resource_id][0]
            if 'SR' in row['DigFile Calc'].strip():
                resource_id_to_update['audio'] += 1
            else:
                resource_id_to_update['moving_image'] += 1
                       
    resource_ids_counter = Counter(resource_ids)        
    unique_resource_ids = set(resource_ids)
    
    for unique_resource_id in unique_resource_ids:
        print('\nupdating collection-level information for ' + str(resource_id))
        coll_info(base_url, repository_id, session_key, unique_resource_id, resource_ids_counter, resource_ids_to_audio_or_moving_image, resource_ids_to_number_audio_and_number_moving_image)
            

elif args.dsc == True:   
    print('parsing project CSV to update container list')
    items = []
    parts = []

    results = []


    with open(args.project_csv, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
        
            # characterize each row in the spreadsheet
            archival_object_id = row['object id'].strip()
            type_of_archival_object_id = row['Type of obj id'].strip().title()
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
            coll_item_number = row['CollItemNo'].strip()
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
            
            # use pickle get access profile
            access_profiles = pickle.load(open('access_profiles.p', 'rb'))
            
            access_control_id = ''
            try:
                access_control_id = access_profiles[mivideo_id]
                
            except:
                access_control_id = '1876301'
            print('Kaltura Access Control ID: ' + access_control_id)
            
            # 1876301 is reading room
            # 2227181 U-M campus
            accessrestrict = ''
            if access_control_id == '1876301':
                accessrestrict = 'Access to this material is restricted to the reading room of the Bentley Historical Library.'
            elif access_control_id == '2227181':
                accessrestrict = 'Access to this material is restricted to the University of Michigan domain.'
            else:
                accessrestrict = ''    
           
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
                    'item_time': item_time,
                    'accessrestrict': accessrestrict
                }
                items.append(item)
                
            elif type_of_digfile_calc == 'item with parts':
                
                digfile_calc_item = coll_item_number
                
                if digfile_calc_item not in [item['digfile_calc_item'] for item in items]:
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
                        'item_length': item_length
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
                    'item_time': item_time,
                    'accessrestrict': accessrestrict
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
            results.append([item['digfile_calc'], archival_object_id])
        
        elif item['type_of_archival_object_id'] == 'Parent' and item['type_of_digfile_calc'] == 'item with parts':
            print('the corresponding archivesspace archival object is a parent and the row is an item with parts')
            archival_object_id = parent_and_item_with_parts(repository_id, base_url, session_key, item, parts)
            results.append([item['digfile_calc'], archival_object_id])
        
        elif item['type_of_archival_object_id'] == 'Item' and item['type_of_digfile_calc'] == 'item with parts':
            print('the corresponding archivesspace archival object is an item and the row is an item with parts')
            item_and_item_with_parts(repository_id, base_url, session_key, item, parts)
            results.append([item['digfile_calc'], archival_object_id])
        
        elif item['type_of_archival_object_id'] == 'Part' and item['type_of_digfile_calc'] == 'item with parts':
            print('the corresponding archivesspace archival object is a part and the row is an item with parts')
            archival_object_id = part_and_item_with_parts(repository_id, base_url, session_key, item, parts)
            results.append([item['digfile_calc'], archival_object_id])

    print('\nexporting results')
    _, filename_with_extension = os.path.split(args.project_csv)
    filename, file_extension = os.path.splitext(filename_with_extension)
    output_path = os.path.join("results", filename + '-RESULTS' + file_extension)
    if args.output:
        output_path = os.path.join(args.output, output_path)

    with open(output_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['DigFile Calc', 'archival_object_id'])
        writer.writerows(results)

print("Alright, we're done!")
