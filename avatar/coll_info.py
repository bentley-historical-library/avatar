from datetime import datetime
import json
import requests

def coll_info(base_url, repository_id, session_key, unique_resource_id, resource_ids_counter, resource_ids_to_audio_or_moving_image):
    
    print('  - GETting resource ' + str(unique_resource_id))
    endpoint = '/repositories/' + str(repository_id) + '/resources/' + str(unique_resource_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)
    
    resource = response.json()
    
    print('\n- Appending extent')

    resource['extents'].append(
        {
            'portion': 'whole',
            'number': str(resource_ids_counter[unique_resource_id]),
            'extent_type': 'digital audiovisual files'
        }
    )
    
    print('\n- Appending "Processing Information" note')
    
    resource['notes'].append(
        {
            'jsonmodel_type': 'note_multipart',
            'type': 'processinfo',
            'subnotes': [{
                'jsonmodel_type': 'note_text',
                'content': '<extptr href="digitalproc" show="embed" actuate="onload">',
            }],
        }
    )
    
    print('\n- Appending revision statement')
    
    resource['revision_statements'].append(
        {
            'date': str(datetime.now().date()),
            'description': 'Revised Extent Note, Processing Information Note and Existence and Location of Copies Note.',
            'jsonmodel_type': 'revision_statement',
        }
    )        
    resource['revision_statements'].append(
        {
            'date': str(datetime.now().date()),
            'description': 'Added links to digitized content.',
            'jsonmodel_type': 'revision_statement',
        }
    )
    resource['revision_statements'].append(
        {
            'date': str(datetime.now().date()),
            'description': 'Added Conditions Governing notes for digitized content.',
            'jsonmodel_type': 'revision_statement',
        }
    )
    
    print('\n- Appending "Existence and Locations of Copies" notes')
    
    resource['notes'].append(
        {
            'jsonmodel_type': 'note_multipart',
            'type': 'altformavail',
            'subnotes': [{
                'jsonmodel_type': 'note_text',
                'content': 'Digitization: A number of recordings within this collection have been digitized. The resulting files are available for playback online or in the Bentley Library Reading Room according to rights. Original media are only available for staff use.',
            }],
        }
    )
    
    print('\n- Appending Genre / Form')
    
    audio = [resource_id_to_audio_or_moving_image['audio'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == unique_resource_id][0]
    moving_image = [resource_id_to_audio_or_moving_image['moving_image'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == unique_resource_id][0]
    
    # {'ref': '/subjects/3144'} is "sound recordings" from AAT
    if audio == True:
        if "/subjects/3144" not in [subject['ref'] for subject in resource['subjects']]:
            resource['subjects'].append({'ref': '/subjects/3144'})
    
    # {'ref': '/subjects/3208'} is "video recordings" from AAT
    if moving_image == True:
        if "/subjects/3208" not in [subject['ref'] for subject in resource['subjects']]:
            resource['subjects'].append({'ref': '/subjects/3208'})
    
    print('  - POSTing resource ' + str(unique_resource_id))
    endpoint = '/repositories/' + str(repository_id) + '/resources/' + str(unique_resource_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(resource))
    print(response.text)
    