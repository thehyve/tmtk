"""tmtk - A toolkit for ETL curation for the tranSMART data warehouse."""
from tmtk.study import Study
from tmtk.params import *
from tmtk.clinical import *
from tmtk.annotation import *
from tmtk.highdim import *
from tmtk.utils import *
import tmtk.toolbox as Toolbox


__version__ = '0.1.0'
__author__ = 'Jochem Bijlard <j.bijlard@gmail.com>'
__all__ = []


if __name__ == '__main__':
    print('This is not meant to run directly.')
