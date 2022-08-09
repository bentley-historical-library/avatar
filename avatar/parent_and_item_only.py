import json
import os
import requests

def parent_and_item_only(repository_id, base_url, session_key, item, base_preservation_path):
    print('\n- creating a child archival object (including instance with top container)')
    
    print('  - GETting archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    instance_type = ''
    top_container_id = ''
    try:
        instance_type = archival_object['instances'][0]['instance_type']
        top_container_id = archival_object['instances'][0]['sub_container']['top_container']['ref'].split('/')[-1]
    except:
        print('it appears that there are no instances on archival object id ' + item['archival_object_id'] + '!')
    
    title = item['item_title']
    if item['item_part_title']:
        title = title + ' ' + item['item_part_title']
    
    proto_item = {
        'jsonmodel_type': 'archival_object',
        'resource': {
            'ref': '/repositories/' + str(repository_id) + '/resources/' + str(item['resource_id'])
        },
        'parent': {
            'ref': '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
        },
        'title': title,
        'component_id': item['digfile_calc_item'],
        'level': 'file',
        'dates': [
            {
                'label': 'creation',
                'expression': item['item_date'],
                'date_type': 'inclusive'
            }
        ],
        'extents': [
            {
                'portion': 'whole',
                'number': '1',
                'extent_type': item['extent_type'],
                'physical_details': '',
                'dimensions': ''
            }
        ],
        'notes': [],
    }
    
    if instance_type:
        proto_item['instances'] = [{
                'jsonmodel_type': 'instance',
                'instance_type': instance_type,
                'sub_container': {
                    'jsonmodel_type': 'sub_container',
                    'top_container': {'ref': '/repositories/' + str(repository_id) + '/top_containers/' + top_container_id}
                }
            }]
    
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
    proto_item['extents'][0]['physical_details'] = physical_details
    dimensions = []
    if item['reel_size']:
        dimensions.append(item['reel_size'])
    if item['item_length']:
        dimensions.append(item['item_length'])
    if item['item_source_length']:
        dimensions.append(item['item_source_length'])
    dimensions = ', '.join(dimensions)  
    proto_item['extents'][0]['dimensions'] = dimensions
    
    if item['reel_size']:
        proto_item['extents'][0]['dimensions'] = item['reel_size']
        
    if item['note_content']:
        proto_item['notes'].append(
            {
                'jsonmodel_type': 'note_singlepart',
                'type': 'abstract',
                'publish': True,
                'content': [item['note_content']]
            }
        )
    if item['accessrestrict']:
        proto_item['notes'].append(
            {
                'jsonmodel_type': 'note_multipart',
                'type': 'accessrestrict',
                'publish': True,
                'subnotes': [
                    {
                        'jsonmodel_type': 'note_text',
                        'content': item['accessrestrict']
                    }
                ]
            }
        )
    if item['note_technical']:
        proto_item['notes'].append(
            {
                'jsonmodel_type': 'note_multipart',
                'type': 'odd',
                'publish': False,
                'subnotes': [
                    {
                        'jsonmodel_type': 'note_text',
                        'content': item['note_technical']
                    }
                ]
            }
        )
    if item['item_time']:
        proto_item['notes'].append(
            {
                'jsonmodel_type': 'note_multipart',
                'type': 'odd',
                'publish': True,
                'subnotes': [
                    {
                        'jsonmodel_type': 'note_text',
                        'content': 'Duration: ' + item['item_time']
                    }
                ]
            }
        )
        
    print('  - POSTing archival object on parent ' + item['archival_object_id'])
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects'
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(proto_item))
    print(response.text)
    
    child_archival_object = response.json()
    child_archival_object_id = child_archival_object['id']
    
    print('- if not a duplicate, creating and linking a digital object (preservation) to the child archival object')
    
    if item['mivideo_id']:
        print('  - GETting archival object ' + str(child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.get(base_url + endpoint, headers=headers)
        print(response.text)
        
        child_archival_object = response.json()
        
        title = child_archival_object['display_string'] + ' (Preservation)'
        
        file_uri = ''
        collection_id = item['digfile_calc'].split('-')[0]
        if item['audio_or_moving_image'] == 'audio':
            file_uri = os.path.join(base_preservation_path, 'AV Collections', 'Audio', collection_id, item['digfile_calc_item'])
        elif item['audio_or_moving_image'] == 'moving image':
            file_uri = os.path.join(base_preservation_path, 'AV Collections', 'Moving Image', collection_id, item['digfile_calc_item'])
        
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
        
        print('  - GETting child archival object ' + str(child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.get(base_url + endpoint, headers=headers)
        print(response.text)
        
        child_archival_object = response.json()
        
        child_archival_object['instances'].append(
            {
                'instance_type': 'digital_object',
                'digital_object': {'ref': digital_object_preservation_uri}
            }
        )
        
        print('  - POSTing child archival object ' + str(child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(child_archival_object))
        print(response.text)
    
    print('- if it exists, creating and linking digital object (access) to the child archival object')
    
    print('  - GETting archival object ' + str(child_archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    child_archival_object = response.json()
    
    title = child_archival_object['display_string'] + ' (Access)'
    
    if item['mivideo_id']:
        proto_digital_object_access = {
            'jsonmodel_type': 'digital_object',
            'repository': {
                'ref': '/repositories/' + str(repository_id)
            },
            'title': title,
            'digital_object_id': item['mivideo_id'],
            'file_versions': [
                {
                    'jsonmodel_type': 'file_version',
                    'file_uri': 'https://bentley.mivideo.it.umich.edu/media/t/' + item['mivideo_id'],
                    'xlink_actuate_attribute': 'onRequest',
                    'xlink_show_attribute': 'new'
                }
            ]
        }
        
        print('  - POSTing digital object (access)')
        endpoint = '/repositories/' + str(repository_id) + '/digital_objects'
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(proto_digital_object_access))
        print(response.text)
        
        digital_object_access = response.json()
        digital_object_access_uri = digital_object_access['uri']
        
        print('  - GETting child archival object ' + str(child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.get(base_url + endpoint, headers=headers)
        print(response.text)
        
        child_archival_object = response.json()
        
        child_archival_object['instances'].append(
            {
                'instance_type': 'digital_object',
                'digital_object': {'ref': digital_object_access_uri}
            }
        )
        
        print('  - POSTing child archival object ' + str(child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(child_archival_object))
        print(response.text)
    
    return child_archival_object_id
