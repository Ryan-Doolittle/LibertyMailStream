import os
import sys



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(".")

    if hasattr(sys, '_MEIPASS'):
        path = os.path.join(base_path, 'src', relative_path)
    else:
        path = os.path.join(base_path, 'src', relative_path)
    print(path)
    return path
