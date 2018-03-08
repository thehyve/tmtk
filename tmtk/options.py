
def type_validator(type_):

    def inner(value):
        if type(value) != type_:
            msg = "Value must have type '{!r}'"
            raise ValueError(msg.format(type_))

    inner.allowed_values = type_
    return inner


is_bool = type_validator(bool)
is_str = type_validator(str)


class OptionWrapper:
    """
    Container for package wide options.
    """
    __opt_dict__ = {}


options = OptionWrapper()


def register_option(key, default, doc=None, validator=None, callback=None):
    """
    Add options to OptionWrapper as properties with a setter that can invoke
    a validator and callback function.

    :param key: name for the option.
    :param default: default value is mandatory.
    :param doc: docstrings are shown for the properties.
    :param validator: callable that checks input for setter,
        should raise ValueError otherwise.
    :param callback: callable
    """

    def getter_(self):
        return self.__opt_dict__[key]

    def setter_(self, value):

        if validator:
            validator(value)

        if callback:
            callback(key, value)

        self.__opt_dict__[key] = value

    doc_prefix = 'Default value: {}\n'.format(default)
    if validator:
        try:
            validator(default)
        except ValueError:
            raise ValueError('Incompatible default value for option {!r}.'.format(key))

        if hasattr(validator, 'allowed_values'):
            doc_prefix = '{}Allowed values: {}\n'.format(doc_prefix, validator.allowed_values)
    doc = doc_prefix + doc

    OptionWrapper.__opt_dict__[key] = default
    prop_ = property(fget=getter_, fset=setter_, doc=doc)
    setattr(OptionWrapper, key, prop_)


transmart_batch_mode_doc = """
Set this to True before creating the tmtk.Study object to prevent 
creation of parameters invalid for usage with transmart-batch. 
To be omitted are support for modifiers, trial visits, and ontology mapping.
"""

register_option('transmart_batch_mode', default=False, doc=transmart_batch_mode_doc, validator=is_bool)
register_option('strict_paths_mode', default=True, doc='\nNot used currently.', validator=is_bool)
register_option('arborist_url', default='http://localhost:25482', doc='\nNot used currently.', validator=is_str)

