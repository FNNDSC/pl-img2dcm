from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'img2dcm',
    version          = '1.0.10',
    description      = 'An app to convert an input image to a DICOM file',
    long_description = readme,
    author           = 'FNNDSC',
    author_email     = 'dev@babyMRI.org',
    url              = 'http://wiki',
    packages         = ['img2dcm'],
    install_requires = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.6',
    entry_points     = {
        'console_scripts': [
            'img2dcm = img2dcm.__main__:main'
            ]
        }
)
