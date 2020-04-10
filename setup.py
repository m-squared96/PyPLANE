from setuptools import setup
from PyPLANE.core_info import VERSION

setup (
    name = "PyPLANE",
    packages = ["PyPLANE", "PyPLANE_styles"],
    version = VERSION,
    scripts = ['bin/run.py'],
    license = "GPL V3",
)
