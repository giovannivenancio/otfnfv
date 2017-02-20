import os
from setuptools import setup

if os.geteuid():
    print ("This script must be run as root!")
    exit(1)

setup(
    install_requires = [
        'pymongo',
        'pillow',
        'python-PIL',
        'python-imaging-tk',
        'ImageTk',
        'python-dateutil',
        'matplotlib',
        'pyparsing',
        'cycler',
        'functools32'
    ])

#LIMPAR DIRETORIOS E ARQUIVOSW CRIADOS
