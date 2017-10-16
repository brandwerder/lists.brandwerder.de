from zope.component import getUtility
from zope.interface import implementer
from mailman.core.i18n import _
from mailman.interfaces.archiver import ArchivePolicy
from mailman.interfaces.styles import IStyle, IStyleManager
from mailman.interfaces.mailinglist import SubscriptionPolicy
from ..templates.brandwerder_template import BrandwerderTemplate
from public import public
import re

# print(__file__ + " called")

@public
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
        return 'Klasse ' + klasse

    def apply(self, mailing_list):
        mlist = mailing_list

        # apply default options
        manager = getUtility(IStyleManager)
        manager.get('legacy-default').apply(mlist)

        ## List Identity

        mlist.display_name = re.sub(r'klasse-(.*)', BrandwerderStyle.klassenlist_name, mlist.list_name)
        mlist.preferred_language = 'de'
        mlist.subject_prefix = _('[$mlist.display_name] ')

        # Description
        mlist.description = _('Die Mailingliste der $mlist.display_name')

        # Information
        mlist.info = _("""Die Mailingliste der $mlist.display_name""")

        # Show list on index page
        mlist.advertised = False

        ## Archiving
        mlist.archive_policy = ArchivePolicy.never

        ## Subscription Policy
        mlist.subscription_policy = SubscriptionPolicy.confirm_then_moderate

        # IMPORTANT: add the template after setting the style, otherwise the
        # changes will not apply?
        if re.match('klasse', mlist.list_name):
            # print('add template: ' + mlist.list_id)
            BrandwerderTemplate.set_template('list:user:notice:welcome', mlist.list_id, 'list:user:notice:welcome-klasse.txt')
