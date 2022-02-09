from distutils.core import setup
import py2exe

setup(
    options={'py2exe': {
        "includes": ["lxml._elementpath"]
    }},
    console=['main.py']
)
