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
    
    print('- if it does not exist, creating and linking a digital object (preservation) to the parent archival object')
    
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
    
    print('  - GETting archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    part = [part for part in parts if item['digfile_calc'] == part['digfile_calc_part']][0]
    
    archival_object['title'] = part['item_part_title']
    archival_object['component_id'] = part['digfile_calc_part']
    archival_object['level'] = 'otherlevel'
    archival_object['other_level'] = 'item-part'
    
    archival_object['dates'].append(
        {
            'label': 'creation',
            'expression': part['item_date'],
            'date_type': 'inclusive'
        }
    )
    
    if part['note_content']:
        abstracts = [note for note in archival_object['notes'] if note['type'] == 'abstract']
        if len(abstracts) == 0:
            archival_object['notes'].append(
                {
                    'jsonmodel_type': 'note_singlepart',
                    'type': 'abstract',
                    'content': [part['note_content']]
                }
            )
        else:
            # not sure how safe this assumption is...
            abstracts[0]['content'] = [part['note_content']]
    # conditions governing access placeholder
    if part['note_technical']:
        archival_object['notes'].append(
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
        archival_object['notes'].append(
            {
                'jsonmodel_type': 'note_singlepart',
                'type': 'physfacet',
                'content': [physical_facet]
            }
        )
        
    print('  - POSTing archival object ' + str(item['archival_object_id']))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(archival_object))
    print(response.text)
    
    archival_object = response.json()
    archival_object_id = archival_object['id']
    
    print('  - GETting archival object ' + str(archival_object_id))
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    archival_object = response.json()
    
    title = archival_object['display_string'] + ' (Access)'
    
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
        
        print('  - GETting child archival object ' + str(archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
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
        
        print('  - POSTing child archival object ' + str(archival_object_id))
        endpoint = '/repositories/' + str(repository_id) + '/archival_objects/' + str(archival_object_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(child_archival_object))
        print(response.text)
    print('- if it exists, creating and linking digital object (access) to the archival object')
    
    return archival_object_id # <-- UPDATE!
