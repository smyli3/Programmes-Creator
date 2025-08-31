#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='snowsports-manager',
    version='0.1.0',
    description='Snowsports Program Manager - A comprehensive management system for snowsports programs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Adam Smylie',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/snowsports-program-manager',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Topic :: Education',
        'Topic :: Office/Business',
    ],
    entry_points={
        'console_scripts': [
            'snowsports=run:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/snowsports-program-manager/issues',
        'Source': 'https://github.com/yourusername/snowsports-program-manager',
    },
)
