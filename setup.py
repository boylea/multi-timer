"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['snail_timer.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True,
    'includes': ['sip', 'PyQt4']}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
