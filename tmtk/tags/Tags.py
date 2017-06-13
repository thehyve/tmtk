import pandas as pd
import os
from ..utils import Exceptions, FileBase, Mappings, path_converter, TransmartBatch, ValidateMixin
from ..params import TagsParams


class MetaDataTags(FileBase, ValidateMixin):
    def __init__(self, params=None, parent=None):
        if params and params.is_viable() and params.datatype == 'tags':
            self.path = os.path.join(params.dirname, params.TAGS_FILE)
        else:
            raise Exceptions.ClassError(type(params), TagsParams)

        self.params = params
        self.parent = parent
        super().__init__()

    def __str__(self):
        return 'Metadata tags: ({})'.format(self.params.path)

    def __repr__(self):
        return 'Metadata tags: ({})'.format(self.params.path)

    @property
    def tag_paths(self):
        """
        Return tag paths delimited by the path_converter.
        """
        return self.df.iloc[:, 0].apply(lambda x: self._convert_path(x))

    @property
    def invalid_paths(self):
        delimiter = Mappings.EXT_PATH_DELIM

        # All paths in study that tags can be mapped to
        study_paths = [node.path for node in self.parent.concept_tree.nodes if node.type != 'tag']

        # Add delimiter to both paths comparing so tag_path only matches if a complete node is matched
        study_paths = ['{0}{1}{0}'.format(delimiter, path_converter(path, internal=False)) for path in study_paths]

        # Add study level path (no nodes)
        study_paths.append(delimiter)

        # Modify tag paths to always end with a single delimiter
        tag_paths = [path.rstrip(delimiter) + delimiter for path in self.tag_paths]  # Ensure single trailing delim

        # Return list of tags that are not mapped to any path
        return [p for p in tag_paths if not any([sp.startswith(p) for sp in study_paths])]

    @staticmethod
    def _convert_path(x):
        starts_with_delim = x.startswith(Mappings.PATH_DELIM) or x.startswith(Mappings.EXT_PATH_DELIM)
        x = path_converter(x, internal=False)
        if starts_with_delim:
            x = Mappings.EXT_PATH_DELIM + x
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

    @staticmethod
    def create_df():
        df = pd.DataFrame(dtype=str, columns=Mappings.tags_header)
        return df

    @property
    def load_to(self):
        return TransmartBatch(param=self.params.path,
                              items_expected=self._get_lazy_batch_items()
                              ).get_loading_namespace()

    def _get_lazy_batch_items(self):
        return {self.params.path: [self.path]}

    def _validate_tag_paths(self):
        invalids = self.invalid_paths
        if invalids:
            self.msgs.error("Tags ({}) found that cannot map to tree.".format(len(invalids)), warning_list=invalids)
        else:
            self.msgs.okay("No tags found that do not map to tree. Total number of tags: {}".format(len(self.tag_paths)))