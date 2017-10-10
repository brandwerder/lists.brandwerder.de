from ..styles.brandwerder_style import BrandwerderStyle

from zope.component import getUtility
from mailman.interfaces.styles import IStyleManager
manager = getUtility(IStyleManager)

#for style in manager.styles:
#    print(style.name)
#print()

# prevent double inclusion
if manager.get('brandwerder-style') is None:
    manager.register(BrandwerderStyle())
