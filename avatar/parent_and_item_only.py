import json
import requests

def parent_and_item_only(repository_id, base_url, session_key, item):
    print('- creating a child archival object (including instance with top container)')
    
    title = item['item_title']
    if item['item_part_title']:
        title = title + ' ' + item['item_part_title']
    
    item_json = {
        'jsonmodel_type': 'archival_object',
        'resource': {
            'ref': '/repositories/' + str(repository_id) + '/resources/' + str(item['resource_id'])
        },
        'parent': {
            'ref': '/repositories/' + str(repository_id) + '/archival_objects/' + str(item['archival_object_id'])
        },
        'title': title,
        'component_id': item['digfile_calc'],
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
                'physical_details': item['av_type'],
                'dimensions': ''
            }
        ],
        'notes': []
    }
    
    if item['reel_size']:
        item_json['extents'][0]['dimensions'] = item['reel_size']
        
    if item['note_content']:
        item_json['notes'].append(
            {
                'jsonmodel_type': 'note_singlepart',
                'type': 'abstract',
                'content': item['note_content']
            }
        )
    # conditions governing access placeholder
    if item['note_technical']:
        item_json['notes'].append(
            {
                'jsonmodel_type': 'note_multipart',
                'publish': False,
                'type': 'odd',
                'subnotes': [
                    {
                        'jsonmodel_type': 'note_text',
                        'content': item['note_technical']
                    }
                ]
            }
        )
    physical_facet = []
    if item.get('fidelity'):
        physical_facet.append(item['fidelity'])
    if item.get('reel_size'):
        physical_facet.append(item['reel_size'])
    if item.get('tape_speed'):
        physical_facet.append(item['tape_speed'])
    if item.get('item_source_length'):
        physical_facet.append(item['item_source_length'])
    if item.get('item_polarity'):
        physical_facet.append(item['item_polarity'])
    if item.get('item_color'):
        physical_facet.append(item['item_color'])
    if item.get('item_sound'):
        physical_facet.append(item['item_sound'])
    if item.get('item_length'):
        physical_facet.append(item['item_length'])
    if item.get('item_time'):
        physical_facet.append(item['item_time'])
    physical_facet = ', '.join(physical_facet)
    if physical_facet:
        item_json['notes'].append(
            {
                'jsonmodel_type': 'note_singlepart',
                'type': 'physfacet',
                'content': physical_facet
            }
        )
        
    print('POSTing archival object on parent ' + item['archival_object_id'])
    endpoint = '/repositories/' + str(repository_id) + '/archival_objects'
    headers = {'X-ArchivesSpace-Session': session_key}
    # response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(item_json))
    # print(response.text)
    
    # child_archival_object = response.json()
    # child_archival_object_id = child_archival_object['id']
    # child_archival_object_uri = child_archival_object['uri']
    
    print('- creating and linking a digital object (preservation) to the child archival object')
    print('- if it exists, creating and linking digital object (access) to the child archival object')
    
    # return child_archival_object_id
