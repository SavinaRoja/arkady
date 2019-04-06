# coding: utf-8

from setuptools import setup

requires = ['pyzmq']


def load_readme():
    with open('README.md') as f:
        readme = f.read()
    return readme


setup(name='arkady',
      version='0.0.1',
      description='A framework for remote device management',
      author='Paul Barton',
      author_email='pablo.barton@gmail.com',
      license='GPL3',
      package_dir={'': 'src'},
      packages=['arkady'],
      install_requires=requires,
      long_description=load_readme(),
      #long_description_content_type='text/markdown',
      classifiers=["Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Operating System :: OS Independent",
                   ]
      )
