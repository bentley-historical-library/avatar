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
        'digital_object_id': item['digfile_calc'],
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
    
    print('- creating a child archival object to the child archival object for the part')
    
    print('  - GETting child archival object ' + str(child_archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    child_archival_object = response.json()
    
    child_instance_type = child_archival_object['instances'][0]['instance_type']
    child_top_container_id = child_archival_object['instances'][0]['sub_container']['top_container']['ref'].split('/')[-1]
    
    part = [part for part in parts if item['digfile_calc'] == part['digfile_calc_part']][0]
    
    proto_part = {
        'jsonmodel_type': 'archival_object',
        'resource': {
            'ref': '/repositories/' + str(repository_id) + '/resources/' + str(item['resource_id'])
        },
        'parent': {
            'ref': '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_archival_object_id)
        },
        'title': part['item_part_title'],
        'component_id': part['digfile_calc_part'],
        'level': 'otherlevel',
        'other_level': 'item-part',
        'dates': [
            {
                'label': 'creation',
                'expression': part['item_date'],
                'date_type': 'inclusive'
            }
        ],
        'notes': []
    }
    
    if part['note_content']:
        proto_part['notes'].append(
            {
                'jsonmodel_type': 'note_singlepart',
                'type': 'abstract',
                'content': [part['note_content']]
            }
        )
    # conditions governing access placeholder
    if part['note_technical']:
        proto_part['notes'].append(
            {
                'jsonmodel_type': 'note_multipart',
                'type': 'odd',
                'publish': False,
                'subnotes': [
                    {
                        'jsonmodel_type': 'note_text',
                        'content': part['note_technical']
                    }
                ]
            }
        )
    physical_facet = []
    if part.get('fidelity'):
        physical_facet.append(part['fidelity'])
    if part.get('reel_size'):
        physical_facet.append(part['reel_size'])
    if part.get('tape_speed'):
        physical_facet.append(part['tape_speed'])
    if part.get('item_source_length'):
        physical_facet.append(part['item_source_length'])
    if part.get('item_polarity'):
        physical_facet.append(part['item_polarity'])
    if part.get('item_color'):
        physical_facet.append(part['item_color'])
    if part.get('item_sound'):
        physical_facet.append(part['item_sound'])
    if part.get('item_length'):
        physical_facet.append(part['item_length'])
    if part.get('item_time'):
        physical_facet.append(part['item_time'])
    physical_facet = ', '.join(physical_facet)
    if physical_facet:
        proto_part['notes'].append(
            {
                'jsonmodel_type': 'note_singlepart',
                'type': 'physfacet',
                'content': [physical_facet]
            }
        )
        
    print('  - POSTing archival object on child ' + str(child_archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects'
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(proto_part))
    print(response.text)
    
    child_of_child_archival_object = response.json()
    child_of_child_archival_object_id = child_of_child_archival_object['id']
    
    print('- if it exists, creating and linking digital object (access) to the child archival object of the child archival object')
    
    print('  - GETting child of child archival object ' + str(child_of_child_archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_of_child_archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    child_of_child_archival_object = response.json()
    
    title = child_of_child_archival_object['display_string'] + ' (Access)'
    
    if part['mivideo_id']:
        proto_digital_object_access = {
            'jsonmodel_type': 'digital_object',
            'repository': {
                'ref': '/repositories/' + str(repository_id)
            },
            'title': title,
            'digital_object_id': part['mivideo_id'],
            'file_versions': [
                {
                    'jsonmodel_type': 'file_version',
                    'file_uri': 'https://bentley.mivideo.it.umich.edu/media/t/' + part['mivideo_id'],
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
        
        print('  - GETting child of child archival object ' + str(child_of_child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_of_child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.get(base_url + endpoint, headers=headers)
        print(response.text)
        
        child_of_child_archival_object = response.json()
        
        child_of_child_archival_object['instances'].append(
            {
                'instance_type': 'digital_object',
                'digital_object': {'ref': digital_object_access_uri}
            }
        )
        
        print('  - POSTing child of child archival object ' + str(child_of_child_archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(child_of_child_archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(child_of_child_archival_object))
        print(response.text)
    
    return child_of_child_archival_object_id
