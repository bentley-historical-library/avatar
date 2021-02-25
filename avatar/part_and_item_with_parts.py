import json
import os
import requests

def part_and_item_with_parts(repository_id, base_url, session_key, item, parts):
    print('\n- updating the parent archival object for the item')
    
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
    
    print('  - POSTing parent archival object ' + parent_archival_object_id)
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(parent_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(parent_archival_object))
    print(response.text) 
    
    print('- if it does not  exist, creating and linking a digital object (preservation) to the parent archival object')
    
    print('  - GETting parent archival object ' + str(parent_archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(parent_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    parent_archival_object = response.json()
    
    parent_archival_object_digital_objects = [instance for instance in parent_archival_object['instances'] if instance['instance_type'] == 'digital_object']
    
    # this is probably not the best way to tell if a digital object (preservation) exists
    if len(parent_archival_object_digital_objects) == 0:
        title = parent_archival_object['display_string'] + ' (Preservation)'
        
        file_uri = ''
        collection_id = item['digfile_calc'].split('-')[0]
        if item['audio_or_moving_image'] == 'audio':
            file_uri = os.path.join('R:', os.sep, 'AV Collections', 'Audio', item['digfile_calc_item'])
        elif item['audio_or_moving_image'] == 'moving image':
            file_uri = os.path.join('R:', os.sep, 'AV Collections', 'Moving Image', collection_id, item['digfile_calc_item'])
        
        proto_digital_object_preservation = {
            'jsonmodel_type': 'digital_object',
            'repository': {
                'ref': '/repositories/' + str(repository_id)
            },
            'publish': False,
            'title': title,
            'digital_object_id': item['digfile_calc_item'],
            'file_versions': [
                {
                    'jsonmodel_type': 'file_version',
                    'file_uri': file_uri
                }
            ]        
        }
        
        print('  - POSTing digital object (preservation)')
        endpoint = '/repositories/' + str(repository_id) + '/digital_objects'
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(proto_digital_object_preservation))
        print(response.text)
        
        digital_object_preservation = response.json()
        
        digital_object_preservation_uri = digital_object_preservation['uri']
        
        print('  - GETting parent archival object ' + str(parent_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(parent_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.get(base_url + endpoint, headers=headers)
        print(response.text)
        
        parent_archival_object = response.json()
        
        parent_archival_object['instances'].append(
            {
                'instance_type': 'digital_object',
                'digital_object': {'ref': digital_object_preservation_uri}
            }
        )
        
        print('  - POSTing parent archival object ' + str(parent_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(parent_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(parent_archival_object))
        print(response.text)
    
    else:
        pass
    
    print('- updating archival object for the part')
    print('- if it exists, creating and linking digital object (access) to the archival object')
    
    return 'placeholder' # <-- UPDATE!
