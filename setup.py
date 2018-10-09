import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

PACKAGE_VERSION = '0.9.0'
DESC = "Collection of recipes for finding information in ActiveData"
with open(os.path.join(here, 'README.md')) as fh:
    README = fh.read()

DEPS = [
    'json-e >= 2.3.2',
    'requests >= 2.18.3',
    'six >= 1.11.0',
    'terminaltables >= 3.1.0',
    'pyyaml',
    'beautifulsoup4'
    'flask',
    'markdown',
]

setup(
    name='active-data-recipes',
    version=PACKAGE_VERSION,
    description=DESC,
    long_description=README,
    keywords='mozilla',
    author='Andrew Halberstadt',
    author_email='ahalberstadt@mozilla.com',
    url='https://github.com/ahal/active-data-recipes',
    license='MPL',
    packages=['adr'],
    include_package_data=True,
    install_requires=DEPS,
    entry_points="""
    # -*- Entry points: -*-
    [console_scripts]
    adr = adr.cli:main
    adr-query = adr.query:cli
    adr-gist = adr.export.gist:cli
    adr-test = adr.export.test:cli
    """,
)
