import os
import setuptools
from distutils import log
from setuptools.command.develop import develop
from setuptools.command.install import install

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

# Get the current package version.
version_ns = {}
with open(pjoin(here, 'tmtk', 'version.py')) as f:
    exec(f.read(), {}, version_ns)
    version_string = version_ns['__version__']

with open("requirements.txt", 'r') as f:
    required_packages = f.read().splitlines()

if os.environ.get('READTHEDOCS') == 'True':
    for dependency in ['pandas']:
        for package in required_packages:
            if package.startswith(dependency):
                required_packages.remove(package)


class HookedInstall(install):
    def run(self):
        install.run(self)

        log.info('Attempting to install and enable transmart-aborist extension.')
        log.info('This can be done manually by running.')
        log.info('  $ jupyter nbextension install --py tmtk.arborist')
        log.info('  $ jupyter serverextension enable --py tmtk.arborist')

        try:
            import notebook
        except ImportError:
            log.info("Cannot find module 'notebook'. Aborting automated install.")
            return

        notebook_version = getattr(notebook, '__version__')
        if notebook_version is None or notebook_version < '4.2.0':
            log.info("Version of notebook package should be at least 4.2.0 for Arborist, consider:")
            log.info("    $ pip3 install --upgrade notebook")
            log.info('Aborting automated install.')
            return

        from notebook.nbextensions import install_nbextension_python, enable_nbextension_python
        from notebook.serverextensions import toggle_serverextension_python, validate_serverextension

        enable_nbextension_python('widgetsnbextension', sys_prefix=True)

        install_nbextension_python('tmtk.arborist', sys_prefix=True, overwrite=True)
        toggle_serverextension_python('tmtk.arborist', enabled=True, sys_prefix=True)

        warnings = validate_serverextension('tmtk.arborist')
        if warnings:
            [log.warn(warning) for warning in warnings]
        else:
            log.info('Extension has been enabled.')


class HookedDevelop(develop):
    def run(self):
        develop.run(self)
        log.info('For the Arborist to work you need to install and enable the jupyter serverextension using:')
        log.info('  $ jupyter nbextension install --py tmtk.arborist')
        log.info('  $ jupyter serverextension enable --py tmtk.arborist')


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

    entry_points={
        'console_scripts': [
            'transmart-batch = tmtk.utils.batch.__main__:run_batch'
        ]
    },

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    cmdclass={
        'install': HookedInstall,
        'develop': HookedDevelop
    }
)
