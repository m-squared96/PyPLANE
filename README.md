# PyPLANE

An open source replacement to the traditional DFIELD and PPLANE applications for solving systems of ODEs

![Alt Text](Screenshot_1.png)
![Alt Text](Screenshot_2.png)

## About

PyPLANE is an open source Python application used for the visualisation and (numerical/graphical) solving of systems of
ODEs. PyPLANE is released under the GPL-3.0

## Installing Pyplane

PyPLANE is available on the Snap Store for Linux

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-white.svg)](https://snapcraft.io/pyplane)

## Code of Conduct

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg)](code-of-conduct.md)

The Contributor Covenant has been adopted as a probationary CoC for the PyPLANE project.

## Development environment

Python 3.7 is used for development. Dependencies (listed in requirements.txt) are as follows:

* NumPy 1.17.0
* SymPy 1.4
* SciPy 1.3.1
* Matplotlib 3.1.1
* PyQt5 5.13.0

To generate a consistent development environment for PyPLANE, run the following lines of code:

```bash
python --version # Ensure output says "Python 3.7.X" with X being another number
python -m venv pyplanedev/
cd pyplanedev/
git clone https://github.com/m-squared96/PyPLANE
source bin/activate
pip install -r PyPLANE/requirements.txt
pre-commit install
```

Note that all Python code should be formatted using the Black Python code formatter. This is achieved automatically
through the use of pre-commit hooks.
