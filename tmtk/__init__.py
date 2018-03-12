"""
Copyright (c) 2017  The Hyve B.V.
This file is distributed under the GNU General Public License
  (see accompanying file LICENSE).

tmtk - A toolkit for ETL curation for the tranSMART data warehouse.
"""
from .options import options

from .study import Study
from .toolbox.skinny_loader.export_to_skinny import SkinnyExport
from .version import __version__

__author__ = 'Jochem Bijlard <j.bijlard@gmail.com>'

__all__ = ['arborist', 'Study', 'SkinnyExport', 'toolbox', '__version__', 'options']
