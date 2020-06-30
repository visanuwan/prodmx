import os
import sys
from setuptools import setup

if sys.version_info[:2] < (3,5):
      raise RuntimeError("Python version >=3.5 required.")

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as handle:
        data = handle.read()
    return data

setup(name='prodmx',
      version='0.1.0',
      install_requires=['pandas>=0.25.1',
            'h5py>=2.9.0',
            'numpy>=1.17.2',
            'tqdm>=4.36.1',
            'scipy>=1.3.1'],
      description='Protein Functional Domain Analysis based on Compressed Sparse Matrix',
      long_description=read('README.md'),
      url='https://github.com/visanuwan/prodmx',
      classifiers= [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
      ],
      author='Visanu Wanchai',
      author_email='visanuw86@gmail.com',
      license='MIT',
      packages=['prodmx'],
      package_dir={'prodmx':"prodmx"},
      include_package_data = True,
      package_data = {
            '': ['*.ini'],
      },
      zip_safe=False,
      entry_points={
            'console_scripts': [
                'prodmx-buildDomain = prodmx.build_pro_dom:main',
                'prodmx-buildArchitecture = prodmx.build_pro_arc:main'
            ]
      })