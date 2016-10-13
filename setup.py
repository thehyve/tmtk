import setuptools
import os

required_packages = ['pandas',
                     'rpy2',
                     'ipython',
                     'flask',
                     'jupyter',
                     'requests',
                     'tqdm',
                     ]

if os.environ.get('READTHEDOCS') == 'True':
    for p in ['pandas', 'rpy2']:
        required_packages.remove(p)

setuptools.setup(
    name="tmtk",
    version="0.1.2",
    url="https://www.github.com/thehyve/tmtk/",

    author="Jochem Bijlard",
    author_email="j.bijlard@gmail.com",

    description="A toolkit for ETL curation for the tranSMART data warehouse.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,

    keywords=['transmart', 'etl', 'arborist', 'concept tree'],

    download_url='https://github.com/thehyve/tmtk/tarball/0.1.2/',

    install_requires=required_packages,

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
