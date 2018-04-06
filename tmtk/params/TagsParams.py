from .base import ParamsBase


class TagsParams(ParamsBase):
    @property
    def mandatory(self):
        return {'TAGS_FILE': {
            'helptext': 'Points to the tags file.'
        }
        }

    @property
    def optional(self):
        return {}

    def is_viable(self):
        """

        :return: True if both the column mapping file is located, else returns False.
        """
        if self.get('TAGS_FILE'):
            return True
        else:
            return False
