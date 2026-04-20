"""
Runtime hook: fix shibokensupport crash in frozen builds.

PySide6's shibokensupport installs a meta-path import hook that calls
inspect.getsource() on every imported module to detect PySide usage.
In a frozen build, calling inspect.getsource() on six._SixMetaPathImporter
fails with AttributeError (repr() tries to access ._path which doesn't exist)
rather than the OSError/TypeError that shibokensupport catches.

Patch inspect.getsource() to return '' for any module that cannot be
inspected in a frozen environment. shibokensupport then sees no 'PySide'
in the source and correctly concludes the module doesn't use PySide.
"""
import inspect as _inspect

_orig_getsource = _inspect.getsource


def _safe_getsource(object):
    try:
        return _orig_getsource(object)
    except Exception:
        return ''


_inspect.getsource = _safe_getsource
