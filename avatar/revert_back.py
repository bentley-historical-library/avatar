def revert_back(base_url, repository_id, resource_ids_set, digfile_calcs):
    for resource_id in resource_ids_set:
        print('- Reverting collection-level updates for resource ' + str(resource_id))
    
    for digfile_calc in digfile_calcs:
        print('- Reverting component-level updates for DigFile Calc ' + digfile_calc)