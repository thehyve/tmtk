import setuptools
from setuptools.command.install import install
from setuptools.command.develop import develop

import os
import subprocess
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
                     'jupyter>=1.0.0',
                     'jupyter-client>=5.0.0',
                     'jupyter-core>=4.3.0',
                     'requests',
                     'tqdm',
                     'mygene>=3.0.0'
                     ]

if os.environ.get('READTHEDOCS') == 'True':
    for p in ['pandas']:
        required_packages.remove(p)


def _ask_for_extension_install():
    print('\nFor the Arborist to work we need to install a jupyter serverextension using:')
    print(' - jupyter nbextension install --py tmtk.arborist')
    print(' - jupyter serverextension enable --py tmtk.arborist')

    if input("Want to proceed with that (Y/n)? ") in ('Y', 'y', ''):
        subprocess.call(["jupyter", "nbextension", "install", "--py", "tmtk.arborist"])
        subprocess.call(["jupyter", "serverextension", "enable", "--py", "tmtk.arborist"])


class HookedInstall(install):
    def run(self):
        install.run(self)
        _ask_for_extension_install()


class HookedDevelop(develop):
    def run(self):
        install.run(self)
        _ask_for_extension_install()


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

    cmdclass={
        'install': HookedInstall,
        'develop': HookedDevelop
    }
)
