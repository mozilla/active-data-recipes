from setuptools import setup

PACKAGE_VERSION = '0.2'
DESC = "Collection of recipes for finding information in ActiveData"
with open('README.md') as fh:
    README = fh.read()

DEPS = [
    'requests >= 2.18.3',
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
    adr = adr.main:cli
    """,
)
