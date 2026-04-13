import gettext

lang = 'ru'

tr = gettext.translation('messages', localedir='locale', languages=[lang])
_ = tr.gettext
_n = tr.ngettext

def report_words(count):

    template = _("Entered {} word(s)")
    print(template.format(count))

def report_words_plural(n):
    msg = _n("Entered {} word", "Entered {} words", n)
    print(msg.format(n))

if __name__ == '__main__':
    n = 5
    report_words(n)
    report_words_plural(n)