import pandas as pd
import os
from ..utils import Exceptions, FileBase, MessageCollector, summarise, Mappings, path_converter
from ..params import TagsParams


class MetaDataTags(FileBase):
    def __init__(self, params=None, parent=None):
        if params and params.is_viable() and params.datatype == 'tags':
            self.path = os.path.join(params.dirname, params.TAGS_FILE)
        else:
            raise Exceptions.ClassError(type(params), TagsParams)

        self.parent = parent
        super().__init__()

    @property
    def tag_paths(self):
        """
        Return tag paths delimited by the path_converter.
        """
        return self.df.ix[:, 0].apply(lambda x: self._convert_path(x))

    @property
    def invalid_paths(self):
        invalid = []
        study_paths = [node.path for node in self.parent.concept_tree.nodes if node.type != 'tag']
        for tag_path in self.tag_paths:
            # Add "+" to both paths comparing so tag_path only matches if a complete node
            # is matched, as "Cell-line+Characteristics" starts with "Cell-line+Char"
            if not any(
                    [(p + Mappings.PATH_DELIM).startswith(tag_path + Mappings.PATH_DELIM) for p in
                     study_paths]):
                invalid.append(tag_path)
        return invalid

    @staticmethod
    def _convert_path(x):
        x = path_converter(x)
        return x.strip()

    def get_tags(self):
        """
        generator that gets tags from tags file.

        :return: tuples (<path>, <title>, <description>)
        """

        for path in set(self.tag_paths):
            associated_tags = self.tag_paths == path
            tags_dict = {}
            self.df[associated_tags].apply(lambda x: tags_dict.update({x[1]: (x[2], x[3])}), axis=1)
            yield path, tags_dict

    def validate(self, verbosity=2):

        message = MessageCollector(verbosity=verbosity)
        message.head("Validating Tags:")
        invalid = self.invalid_paths

        if invalid:
            message.error("Tags ({}) found that cannot map to tree: ({})."
                          " You might want to call_boris() to fix them.".
                          format(len(invalid), summarise(invalid)))
        else:
            message.okay("No tags found that do not map to tree. Total number of tags: {}".
                         format(len(self.tag_paths)))

        message.flush()

    @staticmethod
    def create_df():
        df = pd.DataFrame(dtype=str, columns=Mappings.tags_header)
        return df
