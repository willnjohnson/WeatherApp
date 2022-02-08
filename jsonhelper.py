import os
import json

# gets the absolute path to where main.py is
main_path = os.path.dirname(os.path.abspath(__file__))

# open file and reads in contents to Python object
# returns object
def fread(path):
    path = main_path + path

    data = None
    obj = None
    with open(path, 'r') as fin:
        data = fin.read()
        obj = json.loads(data)
    fin.close()
    return obj

# open file and writes in contents of object to file
def fwrite(path, data):
    path = main_path + path

    with open(path, 'w') as fout:
        json.dump(data, fout, indent=2)
    fout.close()

# checks if a path exists and returns - True if exist, False if not exist
def find(path):
    path = main_path + path

    if os.path.exists(path):
        return True
    return False