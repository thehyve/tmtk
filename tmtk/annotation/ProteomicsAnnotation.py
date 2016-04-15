from tmtk.annotation import AnnotationBase


class ProteomicsAnnotation(AnnotationBase):
    """
    Subclass for proteomics annotation
    """

    @property
    def biomarkers(self):
        biomarker_column = self.df.columns[self.df.columns.str.upper() == 'PROBESETID']
        return self.df[biomarker_column]
