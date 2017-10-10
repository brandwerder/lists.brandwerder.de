from zope.interface import implementer
from mailman.interfaces.styles import IStyle
from zope.component import getUtility
from mailman.interfaces.styles import IStyleManager
import re

@implementer(IStyle)
class BrandwerderStyle:
    name = 'brandwerder-style'

    @staticmethod
    def klassenlist_name(match):
        # input: klasse-(a3) or klasse-6a
        klasse = match.group(1).lower()
        # If klasse = a3 return A3
        # If klasse = 6a return 6a
        if klasse[0].isalpha():
            klasse = klasse[0].upper() + klasse[1:]
        return 'Klasse: ' + klasse

    def apply(self, mailing_list):
        # apply default options
        manager = getUtility(IStyleManager)
        manager.get('legacy-default').apply(mlist)

        mlist = mailing_list
        # overide some options
        mlist.display_name = re.sub(r'klasse-(.*)', BrandwerderStyle.klassenlist_name, mlist.list_name)
