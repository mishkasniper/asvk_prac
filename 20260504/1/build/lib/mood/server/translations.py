"""Translation module with gettext and plural forms support."""
import gettext
import os


class Translator:
    """Handles localization using gettext .mo files."""

    def __init__(self, locale_dir=None):
        """Set locale directory; use default if not provided."""
        if locale_dir is None:
            locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
        self.locale_dir = locale_dir
        self.translators = {}

    def get_translator(self, locale):
        """Return gettext translation object for given locale or None."""
        if locale is None or locale == 'en':
            return None
        if locale not in self.translators:
            try:
                trans = gettext.translation('messages', localedir=self.locale_dir, languages=[locale])
            except FileNotFoundError:
                trans = None
            self.translators[locale] = trans
        return self.translators[locale]

    def localize(self, locale, msgid, msgid_plural=None, n=None, **kwargs):
        """Return localized message with possible plural form and substitutions."""
        trans = self.get_translator(locale)
        if trans is None:
            if msgid_plural is not None and n is not None:
                template = msgid if n == 1 else msgid_plural
            else:
                template = msgid
        else:
            if msgid_plural is not None and n is not None:
                template = trans.ngettext(msgid, msgid_plural, n)
            else:
                template = trans.gettext(msgid)
        if kwargs:
            return template.format(**kwargs)
        return template
