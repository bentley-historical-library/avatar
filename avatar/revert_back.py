import json
import os
import pickle
import requests

def revert_back(base_url, repository_id, session_key, resource_ids_set, digfile_calcs):
    for resource_id in resource_ids_set:
        print('- Reverting collection-level updates for resource ' + str(resource_id))
        
        with open(os.path.join('cache', 'resources', resource_id + '.json'), mode='r') as f:
            resource = json.load(f)
        
        # avoids a "the record you tried to update has been modified since you fetched it" error
        resource['lock_version'] = resource['lock_version'] + 1
            
        print('  - POSTing resource ' + str(resource_id))
        endpoint = '/repositories/' + str(repository_id) + '/resources/' + str(resource_id)
        headers = {'X-ArchivesSpace-Session': session_key}
        response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(resource))
        print(response.text)
    
    for digfile_calc in digfile_calcs:
        print('- Reverting component-level updates for DigFile Calc ' + digfile_calc)
        
        with open(os.path.join('cache', 'digfile_calcs', 'digfile_calcs.p'), mode='rb') as f:
            digfile_calcs_from_pickle = pickle.load(f)
            
        objects_to_update = None
        for digfile_calc_from_pickle in digfile_calcs_from_pickle:
            for digfile_calc_from_pickle_key, digfile_calc_from_pickle_value in digfile_calc_from_pickle.items():
                if digfile_calc_from_pickle_key == digfile_calc:
                    objects_to_update = digfile_calc_from_pickle_value
                    break
                
        for object_to_update in objects_to_update:
            print ('  - Reverting ' + object_to_update['type'] + ' ' + str(object_to_update['id']) + ' (status: ' + object_to_update['status'] + ')') 
            
            if object_to_update['status'] == 'created':

                print('    - DELET[E]ing ' + object_to_update['type'] + ' ' + str(object_to_update['id']))
            
            elif object_to_update['status'] == 'updated':
                # load cached json
                print('    - POSTing ' + object_to_update['type'] + ' ' + str(object_to_update['id']))
            