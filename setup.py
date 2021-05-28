from setuptools import setup
from PyPLANE.core_info import VERSION

setup(
    name="PyPLANE",
    packages=["PyPLANE"],
    version=VERSION,
    scripts=["bin/run.py"],
    license="GPL V3",
    include_package_data=True,
)
