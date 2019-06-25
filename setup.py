#! /usr/bin/env python
try:  # for pip >= 10
   from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
   from pip.req import parse_requirements

from setuptools import find_packages, setup


requires = [str(ir.req) for ir in parse_requirements('requirements.txt',
                                                    session='No Session')]

tests_require = ['pytest-flask', 'pytest-cov']

setup(name='piperci-picli',
      use_scm_version=True,
      description='Commandline client to interact with PiperCI',
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Console',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      author='Nick Wilburn',
      author_email='nwilburn@globalinfotek.com',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points={
        'console_scripts': ['picli=picli.__main__:main']
      },
      install_requires=requires,
      setup_requires=['setuptools-scm'],
      extras_require={'test': tests_require,
                      'uwsgi': ['uwsgi', 'uwsgitop']},
      tests_require=tests_require)

