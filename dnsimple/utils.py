# -*- coding: utf-8 -*-


def get_key(name):
    return '_%s_cached_value' % name


def simple_cached_property(method):
    key = get_key(method.__name__)

    def decorated(self):
        if not hasattr(self, key):
            setattr(self, key, method(self))
        return getattr(self, key)

    decorated.__name__ = 'simple_cached_property(%s)' % method.__name__
    return property(decorated)


def uncache(obj, name):
    try:
        delattr(obj, get_key(name))
    except AttributeError:
        pass
