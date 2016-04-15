from IPython.display import display


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
        self.html = '<h2>{}</h2>'.format(m)


class _Info(CPrint):
    def __init__(self, m):
        self.term = '{}'.format(m)
        self.html = '<p>{}</p>'.format(m)


class _Okay(CPrint):
    def __init__(self, m):
        self.term = '\033[92mOkay: {}\033[0m'.format(m)
        self.html = '<font color="green">&#x2705; {}</font>'.format(m)


class _Warn(CPrint):
    def __init__(self, m):
        self.term = '\033[93mWarning: {}\033[0m'.format(m)
        self.html = '<font color="orange">&#9888; {}</font>'.format(m)


class _Error(CPrint):
    def __init__(self, m):
        self.term = '\033[95m\033[91mError: {}\033[0m'.format(m)
        self.html = '<font color="red">&#x274C; {}</font>'.format(m)

