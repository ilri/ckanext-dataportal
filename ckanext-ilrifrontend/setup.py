from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(
    name='ckanext-ilrifrontend',
    version=version,
    description="Frontend extension (links, logos, etc)",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Carlos Quiros',
    author_email='c.f.quiros@cgiar.org',
    url='http://data.ilri.org',
    license='GPL v3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.ilrifrontend'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        ILRIFrontEnd=ckanext.ilrifrontend.plugin:ILRIFrontEndPlugin
    ''',
)
