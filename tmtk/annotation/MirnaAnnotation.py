from .AnnotationBase import AnnotationBase


class MirnaAnnotation(AnnotationBase):
    """
    Subclass for micro RNA (miRNA) expression annotation files.
    """

    @property
    def biomarkers(self):
        return self.df.ix[:, 0]
