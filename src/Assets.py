import os.path

f = os.path.dirname(__file__).replace('\\', '/') + '/res/'


def res_folder():
    # absolute path to folder `res`
    return f
