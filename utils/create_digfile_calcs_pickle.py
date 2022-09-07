import os
import pickle

dig_file_calcs = []
with open(os.path.join('../', 'cache', 'digfile_calcs', 'digfile_calcs.p'), 'wb') as f:
    pickle.dump(dig_file_calcs, f)
