from .AnnotationBase import AnnotationBase


class MicroarrayAnnotation(AnnotationBase):
    """
    Subclass for microarray (mRNA) expression annotation files.
    """

    @property
    def biomarkers(self):
        return self.df.ix[:, 1]
