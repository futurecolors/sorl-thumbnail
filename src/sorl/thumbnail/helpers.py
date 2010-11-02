import hashlib
import re
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import cache
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.importlib import import_module
from django.utils import simplejson
from sorl.thumbnail.conf import settings


geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailError(Exception):
    pass


def get_or_set_cache(key, callback, timeout=settings.THUMBNAIL_CACHE_TIMEOUT):
    """
    Get value from cache or update with value from callback
    """
    value = cache.get(key)
    if value is None:
        value = callback()
        cache.set(key, value, timeout)
    return value


def toint(number):
    """
    Helper to return best int for a float or just the int it self.
    """
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)


def tokey(*args):
    """
    Computes a (hopefully) unique key from arguments given.
    """
    salt = '||'.join([force_unicode(arg) for arg in args])
    hash_ = hashlib.md5(salt)
    return hash_.hexdigest()


def serialize(obj):
    if isinstance(obj, dict):
        result = SortedDict()
        for key in sorted(obj.keys()):
            result[key]= obj[key]
        obj = result
    return simplejson.dumps(obj)


def deserialize(s):
    return simplejson.loads(s)


def get_module_class(class_path):
    """
    imports and returns module class from ``path.to.module.Class``
    argument
    """
    try:
        mod_name, cls_name = class_path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' %
                                   (mod_name, e)))
    return getattr(mod, cls_name)
