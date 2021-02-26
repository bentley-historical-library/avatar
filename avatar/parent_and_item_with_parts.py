import json
import os
import requests

def parent_and_item_with_parts(repository_id, base_url, session_key, item, parts):
    print('\n- creating a child archival object for the item (including instance with top container)')
    
    print('  - GETting archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    archival_object = response.json()
    
    instance_type = archival_object['instances'][0]['instance_type']
    top_container_id = archival_object['instances'][0]['sub_container']['top_container']['ref'].split('/')[-1]
    
    title = item['item_title']
    
    proto_item = {
        'jsonmodel_type': 'archival_object',
        'resource': {
            'ref': '/repositories/' + str(repository_id) + '/resources/' + str(item['resource_id'])
        },
        'parent': {
            'ref': '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
        },
        'title': title,
        'level': 'otherlevel',
        'other_level': 'item-main',
        'extents': [
            {
                'portion': 'whole',
                'number': '1',
                'extent_type': item['extent_type'],
                'physical_details': item['av_type'],
                'dimensions': ''
            }
        ],
        'instances': [
            {
                'jsonmodel_type': 'instance',
                'instance_type': instance_type,
                'sub_container': {
                    'jsonmodel_type': 'sub_container',
                    'top_container': {'ref': '/repositories/' + str(repository_id) + '/top_containers/' + top_container_id}
                }
            }]
    }
    
    if item['reel_size']:
        proto_item['extents'][0]['dimensions'] = item['reel_size']
        
    print('  - POSTing archival object on parent ' + item['archival_object_id'])
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects'
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(proto_item))
    print(response.text)
    
    child_archival_object = response.json()
    child_archival_object_id = child_archival_object['id']
    
    print('- creating and linking a digital object (preservation) to the child archival object')
    print('- creating a child archival object to the child archival object for the part')
    print('- if it exists, creating and linking digital object (access) to the child archival object of the child archival object')
