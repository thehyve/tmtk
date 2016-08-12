import setuptools

setuptools.setup(
    name="tmtk",
    version="0.1.0",
    url="https://www.github.com/thehyve/tmtk/",

    author="Jochem Bijlard",
    author_email="j.bijlard@gmail.com",

    description="A toolkit for ETL curation for the tranSMART data warehouse.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=['pandas',
                      'rpy2',
                      'ipython',
                      'flask',
                      'jupyter',
                      'requests',
                      'tqdm',
                      ],

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
