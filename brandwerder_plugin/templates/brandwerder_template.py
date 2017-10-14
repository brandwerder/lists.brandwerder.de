from mailman.interfaces.template import ITemplateManager, ALL_TEMPLATES
from zope.component import getUtility
import pathlib
import os

class BrandwerderTemplate:
    name = 'brandwerder-template'

    @staticmethod
    def apply():
        current_dir = os.path.dirname(os.path.abspath(__file__)) + '/de/'
        manager = getUtility(ITemplateManager)
        for name, uri in ALL_TEMPLATES.items():
            if uri is None:
                continue
            file_uri = pathlib.Path(current_dir + uri).resolve().as_uri()
            print(name + ": " + file_uri)
            # manager.set(name, None, file_uri)
