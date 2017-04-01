import setuptools
import os
import re

VERSIONFILE=os.path.join('tmtk', '__init__.py')
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version_string = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {}.".format(VERSIONFILE,))

required_packages = ['pandas',
                     'ipython',
                     'flask',
                     'jupyter',
                     'requests',
                     'tqdm',
                     'mygene>=3.0.0'
                     ]

if os.environ.get('READTHEDOCS') == 'True':
    for p in ['pandas']:
        required_packages.remove(p)

setuptools.setup(
    name="tmtk",
    version=version_string,
    url="https://www.github.com/thehyve/tmtk/",

    author="Jochem Bijlard",
    author_email="j.bijlard@gmail.com",

    description="A toolkit for ETL curation for the tranSMART data warehouse.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,

    keywords=['transmart', 'etl', 'arborist', 'concept tree'],

    download_url='https://github.com/thehyve/tmtk/tarball/{}/'.format(version_string),

    install_requires=required_packages,

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
