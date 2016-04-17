from IPython.display import display
import os


class CPrint:
    def __repr__(self):
        return self.term

    def _repr_html_(self):
        return self.html

    @staticmethod
    def warn(message):
        return display(_Warn(message))

    @staticmethod
    def error(message):
        return display(_Error(message))

    @staticmethod
    def info(message):
        return display(_Info(message))

    @staticmethod
    def head(message):
        return display(_Head(message))

    @staticmethod
    def okay(message):
        return display(_Okay(message))


class _Head(CPrint):
    def __init__(self, m):
        self.term = '\033[1m\033[95m{}\033[0m'.format(m)
        self.html = '<h3>{}</h3>'.format(m)


class _Info(CPrint):
    def __init__(self, m):
        self.term = '{}'.format(m)
        self.html = '<p>{}</p>'.format(m)


class _Okay(CPrint):
    def __init__(self, m):
        self.term = '\033[92mOkay: {}\033[0m'.format(m)
        self.html = '<p><font color="green">&#x2705; {}</font></p>'.format(m)


class _Warn(CPrint):
    def __init__(self, m):
        self.term = '\033[93mWarning: {}\033[0m'.format(m)
        self.html = '<p><font color="orange">&#9888; {}</font></p>'.format(m)


class _Error(CPrint):
    def __init__(self, m):
        self.term = '\033[95m\033[91mError: {}\033[0m'.format(m)
        self.html = '<p><font color="red">&#x274C; {}</font></p>'.format(m)


class MessageCollector:
    def __init__(self, verbosity=5):
        """
        Collect messages to be printed later by CPrint.

        :param verbosity: integer between 0 and 4, where 0 prints nothing, 1 only errors,
        2 warnings, 3 _okay messages, and 4 includes _info messages.
        """
        self._head = []
        self._info = []
        self._okay = []
        self._warn = []
        self._error = []
        self.found_error = False
        self.verbosity = verbosity

    def head(self, message):
        self._head.append(message)

    def info(self, message):
        if self.verbosity > 3:
            self._info.append(message)

    def okay(self, message):
        if self.verbosity > 2:
            self._okay.append(message)

    def warn(self, message):
        if self.verbosity > 1:
            self._warn.append(message)

    def error(self, message):
        self.found_error = True
        if self.verbosity > 0:
            self._error.append(message)

    def flush(self):
        if any([self._info, self._okay, self._warn, self._error]) and self._head:
            CPrint.head(self._head[0])
        if self._error:
            [CPrint.error(m) for m in self._error]
        if self._warn:
            [CPrint.warn(m) for m in self._warn]
        if self._okay:
            [CPrint.okay(m) for m in self._okay]
        if self._info:
            [CPrint.info(m) for m in self._info]
