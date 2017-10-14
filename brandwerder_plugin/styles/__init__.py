from .brandwerder_style import BrandwerderStyle
from ..templates.brandwerder_template import BrandwerderTemplate

print(__file__ + " called")

from zope.component import getUtility
from mailman.interfaces.styles import IStyleManager
manager = getUtility(IStyleManager)

for style in manager.styles:
   print(style.name)
print()

# prevent double inclusion
if manager.get('brandwerder-style') is None:
    manager.register(BrandwerderStyle())
    # BrandwerderTemplate.apply()
