import os

from flash_serve.component import FlashServe

__all__ = ["FlashServe"]

_PACKAGE_ROOT = os.path.dirname(__file__)
TEMPLATES_ROOT = os.path.join(_PACKAGE_ROOT, "templates")