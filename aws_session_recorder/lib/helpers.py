class AlwaysDoNothing(object):
    def __getattr__(self, name):
        def method(*args):
            return None

        return method
