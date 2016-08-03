"""tmtk - A toolkit for ETL curation for the tranSMART data warehouse."""
from .study import Study
from .clinical import Clinical
import tmtk.utils
import tmtk.arborist
import tmtk.params
# import tmtk.annotation
# import tmtk.highdim
import tmtk.toolbox as Toolbox
from .toolbox import wizard

__version__ = '0.1.0'
__author__ = 'Jochem Bijlard <j.bijlard@gmail.com>'
__all__ = []


if __name__ == '__main__':
    print('This is not meant to run directly.')
