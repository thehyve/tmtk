from .AnnotationBase import AnnotationBase
from tmtk.utils.CPrint import CPrint


class ProteomicsAnnotation(AnnotationBase):
    """
    Subclass for proteomics annotation
    """

    @property
    def biomarkers(self):
        probeset_id_column = self.df.columns[self.df.columns.str.upper() == 'PROBESETID']
        if len(probeset_id_column) != 1:
            CPrint.error('Expected a probesetid column but got {}'.format(len(probeset_id_column)))
            return None
        return self.df.ix[:, probeset_id_column[0]]
