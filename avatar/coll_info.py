import json
import requests

def coll_info(base_url, repository_id, session_key, unique_resource_id, resource_ids_counter):
    
    print('  - GETting resource ' + str(unique_resource_id))
    endpoint = '/repositories/' + str(repository_id) + '/resources/' + str(unique_resource_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response.text)

    print('\n- Appending extent')
    print('\n- Appending "Processing Information" note')
    print('\n- Appending revision statement')
