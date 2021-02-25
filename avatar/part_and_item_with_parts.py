import json
import os
import requests

def part_and_item_with_parts(repository_id, base_url, session_key, item, parts):
    print('- updating the parent archival object for the item')
    
    print('  - GETting archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    parent_archival_object_uri = archival_object['parent']['ref']
    parent_archival_object_id = parent_archival_object_uri.split('/')[-1]
    
    print('  - GETting parent archival object ' + str(parent_archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(parent_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    parent_archival_object = response.json()
    
    parent_archival_object['title'] = item['item_title']
    parent_archival_object['level'] = 'otherlevel'
    parent_archival_object['other_level'] = 'item-main'
    
    dimensions = ''
    if item['reel_size']:
        dimensions = item['reel_size']
    parent_archival_object['extents'].append(
        {
            'portion': 'whole',
            'number': '1',
            'extent_type': item['extent_type'],
            'physical_details': item['av_type'],
            'dimensions': dimensions
        }
    )
    
    print('  - POSTing parent archival object on parent ' + parent_archival_object_id)
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(parent_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(parent_archival_object))
    print(response.text) 
    
    print('- creating and linking a digital object (preservation) to the parent archival object')
    print('- updating archival object for the part')
    print('- if it exists, creating and linking digital object (access) to the archival object')
    
    return 'placeholder' # <-- UPDATE!
