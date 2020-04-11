from PyPLANE_styles import styles
import os

 # Define methods to return specific style sheets

def default_light_style():
    """
    The default style that PyPLANE will most likely ship with
    """
    module_dir = os.path.dirname(__file__)
    css_file = os.path.abspath(os.path.join(module_dir, "default_light.css"))
    return open(css_file).read()

def default_dark_style():
    """
    Because dark themes are awesome
    """
    pass
