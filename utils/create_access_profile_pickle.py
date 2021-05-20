import csv
import os
import pickle

access_profiles = {}

with open(os.path.join('../', 'kaltura-access-export', 'kaltura-access-export-20210322.csv')) as f:
    reader = csv.DictReader(f)
    for row in reader:
        mivideo_id = row['entry_id']
        # Based on our conversation, I think you will want to use the access control id field. Note that 876301 is reading room, 1694751 is public, and 2227181 is U-M campus.
        access_control_id = row['accessControlId']
        
        access_profiles[mivideo_id] = access_control_id
        
pickle.dump(access_profiles, open(os.path.join('../', 'access_profiles.p'), 'wb'))
