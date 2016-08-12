"""tmtk - A toolkit for ETL curation for the tranSMART data warehouse."""
from .study import Study
from .clinical import Clinical
from .toolbox import wizard

__version__ = '0.1.0'
__author__ = 'Jochem Bijlard <j.bijlard@gmail.com>'
__all__ = []

if __name__ == '__main__':
    print('This is not meant to run directly.')
