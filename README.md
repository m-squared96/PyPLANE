# PyPLANE

An open source replacement to the traditional DFIELD and PPLANE applications for solving systems of ODEs

## About

PyPLANE is an open source Python application used for the visualisation and (numerical/graphical) solving of systems of
ODEs. PyPLANE is released under the GPL-3.0

## Development environment

Dependencies (listed in requirements.txt) are as follows:
* NumPy 1.17.0
* SymPy 1.4
* SciPy 1.3.1
* Matplotlib 3.1.1
* PyQt5 5.13.0

To generate a consistent development environment for PyPLANE, run the following lines of code:

```bash
python -m venv pyplanedev/
cd pyplanedev/
git clone https://github.com/m-squared96/PyPLANE
pip install -r PyPLANE/requirements.txt
```
