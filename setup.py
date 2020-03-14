from setuptools import setup

setup(name='prodmx',
      version='beta',
      description='Protein Functional Domain Analysis based on Compressed Sparse Matrix',
      url='https://github.com/visanuwan/prodmx',
      author='Visanu Wanchai',
      author_email='visanuw86@gmail.com',
      license='MIT',
      packages=['prodmx'],
      package_dir={'prodmx':"prodmx"},
      zip_safe=False,
      entry_points={
            'console_scripts': [
                'prodmx-build-dom = prodmx.build_pro_dom:main',
                'prodmx-build-arc = prodmx.build_pro_arc:main'
            ]
      })