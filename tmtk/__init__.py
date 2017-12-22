"""
Copyright (c) 2017  The Hyve B.V.
This file is distributed under the GNU General Public License
  (see accompanying file LICENSE).

tmtk - A toolkit for ETL curation for the tranSMART data warehouse.
"""

from .study import Study
from .toolbox.skinny_loader.export_to_skinny import SkinnyExport


version_info = (0, 4, 1, 'dev0')
__version__ = '.'.join(map(str, version_info))

__author__ = 'Jochem Bijlard <j.bijlard@gmail.com>'

__all__ = ['Study', 'SkinnyExport']
