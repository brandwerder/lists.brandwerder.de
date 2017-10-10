from zope.interface import implementer
from mailman.interfaces.styles import IStyle
@implementer(IStyle)
class BrandwerderStyle:
    name = 'brandwerder-style'
    def apply(self, mailing_list):
        # Just does something very simple.
        mailing_list.display_name = 'TEST STYLE LIST'
