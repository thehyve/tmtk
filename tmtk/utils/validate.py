import logging
from IPython.display import display

from . import cached_property

logger = logging.getLogger('validator')
logging.debug('Loaded logger.')

DEBUG = 'DEBUG'
INFO = 'INFO'
OKAY = 'OKAY'
WARNING = 'WARNING'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'

MSG_RANK = {
    DEBUG: 0,
    INFO: 1,
    OKAY: 2,
    WARNING: 3,
    ERROR: 4,
    CRITICAL: 5
}

TERMINAL_COLOR = {
    DEBUG: '\033[0m',
    INFO: '\033[0m',
    OKAY: '\033[92m',
    WARNING: '\033[93m',
    ERROR: '\033[95m',
    CRITICAL: '\033[95m'
}

HTML_COLOR = {
    DEBUG: 'grey',
    INFO: 'black',
    OKAY: 'green',
    WARNING: 'orange',
    ERROR: 'red',
    CRITICAL: 'purple'
}

HTML_ICON = {
    # DEBUG: '',
    # INFO: 'white',
    OKAY: '&#x2705;',
    WARNING: '&#9888;',
    ERROR: '&#x274C;',
    # CRITICAL: ''
}


class Message:

    def __init__(self, msg=None, level=None, warning_list=None, method=None, silent=False):
        self.level = level or INFO
        self.msg = msg
        self._warning_list = ['{!r}'.format(s) for s in warning_list] if warning_list else None
        if not silent:
            display(self)

    @staticmethod
    def debug(msg, **kwargs):
        Message(level=DEBUG, msg=msg, **kwargs)

    @staticmethod
    def info(msg, **kwargs):
        Message(level=INFO, msg=msg, **kwargs)

    @staticmethod
    def okay(msg, **kwargs):
        Message(level=OKAY, msg=msg, **kwargs)

    @staticmethod
    def warning(msg, **kwargs):
        Message(level=WARNING, msg=msg, **kwargs)

    @staticmethod
    def error(msg, **kwargs):
        Message(level=ERROR, msg=msg, **kwargs)

    @staticmethod
    def critical(msg, **kwargs):
        Message(level=CRITICAL, msg=msg, **kwargs)

    def __str__(self):
        return "[{}] {}".format(self.level, self.msg)

    def __repr__(self):
        response = '{}{}\033[0m'.format(TERMINAL_COLOR[self.level], str(self))

        if self._warning_list:
            response += '\n   list([{}])'.format(', '.join(self._warning_list))

        return response

    def _repr_html_(self):
        html_string = '<font color="{}" style="font-family: monospace;">{} {}</font>'
        response = html_string.format(HTML_COLOR[self.level],
                                      HTML_ICON.get(self.level, ''),
                                      str(self))

        if self._warning_list:
            appendix = '<details style="font-family: monospace;">' \
                       '<summary>See list of {} items:</summary>list([{}])' \
                       '</details>'

            response += appendix.format(len(self._warning_list),
                                        ', '.join(self._warning_list))

        return response


class MessageCollection:
    def __init__(self, message_list=None, head=None):
        self.msgs = message_list or []
        self.head = head or 'MessageCollection'
        self.verbosity = INFO

    def debug(self, msg, warning_list=None):
        self.msgs.append(Message(msg, warning_list=warning_list,
                                 level=DEBUG, silent=self._suppress_messages))

    def info(self, msg, warning_list=None):
        self.msgs.append(Message(msg, warning_list=warning_list,
                                 level=INFO, silent=self._suppress_messages))

    def okay(self, msg, warning_list=None):
        self.msgs.append(Message(msg, warning_list=warning_list,
                                 level=OKAY, silent=self._suppress_messages))

    def warning(self, msg, warning_list=None):
        self.msgs.append(Message(msg, warning_list=warning_list,
                                 level=WARNING, silent=self._suppress_messages))

    def error(self, msg, warning_list=None):
        self.msgs.append(Message(msg, warning_list=warning_list,
                                 level=ERROR, silent=self._suppress_messages))

    def critical(self, msg, warning_list=None):
        self.msgs.append(Message(msg, warning_list=warning_list,
                                 level=CRITICAL, silent=self._suppress_messages))

    def remove_below(self, rank):
        msg_rank = rank if isinstance(rank, int) else MSG_RANK[rank.upper()]
        self.msgs = [msg for msg in self.msgs if MSG_RANK[msg.level] >= msg_rank]

    @property
    def has_error(self):
        return any([MSG_RANK.get(m.level, 0) >= 4 for m in self.msgs])

    @cached_property
    def _suppress_messages(self):
        return False

    @property
    def list_as_html(self):
        return '<ul><li>{}</li></ul>'.format('</li><li>'.join([li._repr_html_() for li in self.msgs]))

    @property
    def list_as_str(self):
        return '\n>> ' + '\n>> '.join([repr(li) for li in self.msgs])

    def _repr_html_(self):
        return '<h3>{}</h3>{}'.format(self.head, self.list_as_html)

    def __repr__(self):
        return '\n{}{}'.format(self.head, self.list_as_str)


class ValidateMixin:

    def _run_validate_method(self, m):
        try:
            getattr(self, m)()

        except Exception as e:
            self.msgs.critical('{!r} for {!r}'.format(e, m))

    @cached_property
    def msgs(self):
        return MessageCollection(head=self)

    def validate(self, verbosity=WARNING):
        """
        Run all validate methods for this object.

        :param verbosity: only display output of this level and above.
            Levels: 'debug', 'info', 'okay', 'warning', 'error', 'critical'.
            Default is 'WARNING'.
        :return: True if no errors or critical is encountered.
        """
        self.msgs.msgs = []
        validate_methods = [m for m in self.__dir__() if m.startswith('_validate_')]
        self.msgs._suppress_messages = True

        try:
            for m in validate_methods:
                self._run_validate_method(m)

        finally:
            self.msgs._suppress_messages = False

        is_valid = not self.msgs.has_error

        self.msgs.remove_below(verbosity)

        if self.msgs.msgs:
            display(self.msgs)

        return is_valid

