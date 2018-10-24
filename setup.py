import re
from setuptools import setup

with open('cloudtts/__init__.py') as f:
    version = re.search('__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='cloudtts',
    version=version,
    author='Mitsuhiro Setoguchi',
    author_email='setoguchi@bengo4.com',
    description='Wrapper Library for Text to Speech API services',
    url='https://github.com/bengo4/cloudtts',
    packages=['cloudtts'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    licence='MIT',
    include_package_data=True,
    platforms='any',
    install_requires=[
        p.strip() for p in open('requirements.txt').readlines()
    ],
)
