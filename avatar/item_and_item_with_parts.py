import json
import os
import requests

def item_and_item_with_parts(repository_id, base_url, session_key, item, parts):
    print('- updating the archival object for the item')
    
    print('  - GETting archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    archival_object['title'] = item['item_title']
    archival_object['level'] = 'otherlevel'
    archival_object['other_level'] = 'item-main'
    
    physical_details = [item['av_type']]
    if item['item_color']:
        physical_details.append(item['item_color'])
    if item['item_polarity']:
        physical_details.append(item['item_polarity'])
    if item['item_sound']:
        physical_details.append(item['item_sound'])
    if item['fidelity']:
        physical_details.append(item['fidelity'])
    if item['tape_speed']:
        physical_details.append(item['tape_speed'])
    physical_details = ', '.join(physical_details)
    dimensions = []
    if item['reel_size']:
        dimensions.append(item['reel_size'])
    if item['item_length']:
        dimensions.append(item['item_length'])
    if item['item_source_length']:
        dimensions.append(item['item_source_length'])
    dimensions = ', '.join(dimensions)  
    archival_object['extents'].append(
        {
            'portion': 'whole',
            'number': '1',
            'extent_type': item['extent_type'],
            'physical_details': physical_details,
            'dimensions': dimensions
        }
    )
    
    print('  - POSTing archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(archival_object))
    print(response.text)
    
    print('- creating and linking a digital object (preservation) to the archival object')
    print('- creating a child archival object for the part')
    print('- if it exists, creating and linking digital object (access) to the child archival object')
