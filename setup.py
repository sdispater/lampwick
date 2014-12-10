# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name='lampwick',
    license='MIT',
    version=__version__,
    description='Simple wrappper around ffmpeg commands.',
    author='Sébastien Eustace',
    author_email='sebastien.eustace@gmail.com',
    url='https://github.com/sdispater/lampwick',
    download_url='https://github.com/sdispater/lampwick/archive/0.1.tar.gz',
    packages=find_packages(),
    install_requires=['nose'],
    tests_require=['nose'],
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
