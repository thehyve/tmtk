from .DataFile import *
from .Variable import *
from .ColumnMapping import *
from .WordMapping import *
import tmtk.utils as utils


class Clinical:
    """
    Container class for all clinical information.
    """
    def __init__(self, clinical_params):
        self.ColumnMapping = ColumnMapping(params=clinical_params)
        self.WordMapping = WordMapping(params=clinical_params)

        for file in self.ColumnMapping.included_datafiles:
            safe_name = utils.clean_for_namespace(file)
            self.__dict__[safe_name] = DataFile(path=os.path.join(clinical_params.dirname, file))
