import os

# from mailman.interfaces.plugin import IPlugin
from public import public
from zope.interface import implementer
from .styles.brandwerder_style import BrandwerderStyle
from .templates.brandwerder_template import BrandwerderTemplate

@public
# @implementer(IPlugin)
class BrandwerderPlugin:
    def pre_hook(self):
        manager.register(BrandwerderStyle())

    def post_hook(self):
        BrandwerderTemplate.apply()

    @property
    def resource(self):
        return None
