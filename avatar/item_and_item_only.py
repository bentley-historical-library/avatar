import json
import os
import requests

def item_and_item_only(repository_id, base_url, session_key, item):
    print('\n- updating the archival object')    
    
    print('  - GETting archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    title = item['item_title']
    if item['item_part_title']:
        title = title + ' ' + item['item_part_title']
    archival_object['title'] = title
    archival_object['level'] = 'file'
    
    archival_object['dates'] = [
        {
            'label': 'creation',
            'expression': item['item_date'],
            'date_type': 'inclusive'
        }
    ]
    
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
    archival_object['extents'] = [
        {
            'portion': 'whole',
            'number': '1',
            'extent_type': item['extent_type'],
            'physical_details': physical_details,
            'dimensions': dimensions
        }
    ]
    
    if item['note_content']:
        abstracts = [note for note in archival_object['notes'] if note['type'] == 'abstract']
        if len(abstracts) == 0:
            archival_object['notes'].append(
                {
                    'jsonmodel_type': 'note_singlepart',
                    'type': 'abstract',
                    'publish': True,
                    'content': [item['note_content']]
                }
            )
        else:
            # not sure how safe this assumption is...
            abstracts[0]['content'] = [item['note_content']]
    if item['accessrestrict']:
        archival_object['notes'].append(
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
        archival_object['notes'].append(
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
        archival_object['notes'].append(
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
        
    print('  - POSTing archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(archival_object))
    print(response.text)
    
    archival_object = response.json()
    archival_object_id = archival_object['id']
    
    print('- creating and linking a digital object (preservation) to the archival object')
    
    print('  - GETting archival object ' + str(archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    title = archival_object['display_string'] + ' (Preservation)'
    
    file_uri = ''
    collection_id = item['digfile_calc'].split('-')[0]
    if item['audio_or_moving_image'] == 'audio':
        file_uri = os.path.join('R:', os.sep, 'AV Collections', 'Audio', collection_id, item['digfile_calc_item'])
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
    
    print('  - GETting  archival object ' + str(archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    archival_object['instances'].append(
        {
            'instance_type': 'digital_object',
            'digital_object': {'ref': digital_object_preservation_uri}
        }
    )
    
    print('  - POSTing archival object ' + str(archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(archival_object))
    print(response.text)
    
    print('- if it exists, creating and linking digital object (access) to the  archival object')
    
    print('  - GETting archival object ' + str(archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    title = archival_object['display_string'] + ' (Access)'
    
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
        
        print('  - GETting archival object ' + str(archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.get(base_url + endpoint, headers=headers)
        print(response.text)
        
        archival_object = response.json()
        
        archival_object['instances'].append(
            {
                'instance_type': 'digital_object',
                'digital_object': {'ref': digital_object_access_uri}
            }
        )
        
        print('  - POSTing archival object ' + str(archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(archival_object))
        print(response.text)
    
    return archival_object_id
    