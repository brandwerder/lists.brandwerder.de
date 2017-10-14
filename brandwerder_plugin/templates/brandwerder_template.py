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
        for k, v in ALL_TEMPLATES:
            if v is None:
                continue
            file_uri = pathlib.Path(current_dir + k).resolve().as_uri()
            print(key + ": " + file_uri)
            # manager.set(k, None, file_uri)
