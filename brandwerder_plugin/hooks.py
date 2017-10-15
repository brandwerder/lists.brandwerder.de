import os

# from mailman.interfaces.plugin import IPlugin
from public import public
from zope.interface import implementer
from .templates.brandwerder_template import BrandwerderTemplate

@public
# @implementer(IPlugin)
class BrandwerderPlugin:
    def pre_hook(self):
        print("pre_hook called")

    def post_hook(self):
        print("post_hook called")
        BrandwerderTemplate.apply()

    @property
    def resource(self):
        return None

# mailman 3.1 pre hook
def pre_hook():
    BrandwerderPlugin().pre_hook()

# mailman 3.1 post hook
def post_hook():
    BrandwerderPlugin().post_hook()
