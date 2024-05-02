import os
import sys



def resource_path(relative_path):
    """
    Generates an absolute path to a resource that works both in development and when the application is 
    frozen using PyInstaller.

    This function constructs an absolute path by appending the provided relative path to the base path of 
    the application. When the application is packaged using PyInstaller, it refers to the temporary folder
    created by PyInstaller. In a development environment, it refers to the project's root directory.

    Args:
        relative_path (str): The relative path to the resource within the project or the temporary directory.

    Returns:
        str: The absolute path to the resource.

    Notes:
        - sys._MEIPASS is used to detect if the application is running in a frozen state (packaged by PyInstaller).
        - This function prints the resolved path, which can help in debugging and verifying the correct paths are being used.
    """
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
