from mailman.interfaces.template import ITemplateManager, ALL_TEMPLATES
from zope.component import getUtility
import pathlib
import os
from public import public

@public
class BrandwerderTemplate:
    name = 'brandwerder-template'

    @staticmethod
    def apply():
        current_dir = os.path.dirname(os.path.abspath(__file__)) + '/de/'
        manager = getUtility(ITemplateManager)
        for name, uri in ALL_TEMPLATES.items():
            if uri is None:
                continue
            file_path = current_dir + uri
            file_uri = pathlib.Path(file_path).resolve().as_uri()
            print(name + ": " + file_path)
            print(name + ": " + file_uri)
            # manager.set(name, None, file_uri)
            template = manager.get(name, None)
            print(template)
            print()
