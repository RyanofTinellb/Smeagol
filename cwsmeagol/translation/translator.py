# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

class Translator:
    def __init__(self, language=None):
        language = language or 'en'
        languages = OrderedDict()
        languages['en'] = English
        languages['hl'] = HighLulani
        languages['vl'] = VulgarLulani
        languages['ef'] = EarlyFezhle
        languages['lf'] = LateFezhle
        languages['kf'] = KoineFezhle
        languages['op'] = OldPtokan
        languages['mp'] = MiddlePtokan
        languages['sp'] = StandardPtokan
        languages['pb'] = PreBrequen
        languages['ab'] = ArchaicBrequen
        languages['cb'] = CommonBrequen
        languages['pz'] = ProtoZhaladi
        languages['cz'] = ContemporaryZhaladi
        languages['rz'] = ReformedZhaladi
        languages['ct'] = ClassicalTsarin
        languages['mt'] = ModernTsarin
        languages['as'] = AncientSolajin
        languages['ms'] = MedievalSolajin
        languages['ts'] = TraditionalSolajin
        languages['ns'] = NewSolajin
        self.number = len(languages)
        self.languages = languages
        self.select(language)

    def select(self, language):
        language = language.lower()
        try:
            self.converter = self.languages[language]()
        except (IndexError, AttributeError, KeyError):
            self.converter = English()
        self.name = self.converter.name
        try:
            self.safename = self.converter.safename
        except AttributeError:
            self.safename = self.converter.name
        self.code = language
        return self.safename

    def encode(self, languagename):
        languagename = languagename.lower()
        for code, language in self.languages.iteritems():
            language = language()
            try:
                if language.urlname == languagename:
                    return code
            except AttributeError:
                name = language.name.lower().replace(' ', '')
                if name == languagename:
                    return code
        else:
            return 'unknown'

    def convert_text(self, text):
        return self.converter.convert_text(text)

    def convert_word(self, text):
        return self.converter.convert_word(text)

    def convert_sentence(self, text):
        return self.converter.convert_sentence(text)


class English:
    def __init__(self):
        self.name = 'English'

    @staticmethod
    def convert_text(text):
        return text

    @staticmethod
    def convert_sentence(text):
        return text

    @staticmethod
    def convert_word(text):
        return text


class HighLulani:
    def __init__(self):
        self.name = 'High Lulani'

    # Converts a transliterated text into High Lulani text
    # See grammar.tinellb.com/highlulani for details.
    @staticmethod
    def convert_text(text):
        if text == '* **':
            return text

        # removes full stops if before a parenthesis
        text = text.replace('.(', '(')

        # removes markdown tags, hyphens, dollars, parentheses and quote marks
        text = re.sub("\[(|/)[a-z]\]|-|[$()]|'\\\"|\\\"", "", text)

        # removes angle brackets and information between them
        text = re.sub(r'<.*?>', '', text)

        # replaces unicode
        text = text.replace('&rsquo;', "'")
        text = text.replace('&#x294;', "''")

        # replaces "upper case" glottal stop with "lower case" apostrophe
        text = re.sub("(\"| |^)''", r"\1'", text)
        text = text.lower()
        output = ""
        for last, this in zip(text, text[1:]):
            if this == last:
                output += ";"
            elif last == "-":
                if this in "aiu":
                    output += "/" + this
            elif last == "'":
                output += this
            elif this == "a":
                output += last
            elif this == "i":
                output += last.upper()
            elif this == "u":
                index = "pbtdcjkgmnqlrfsxh".find(last)
                output += "oOeEyY><UIAWwvzZV"[index]
            elif this == " ":
                if last in ".!?":
                    output += " . "
                elif last in ",;:":
                    output += " , "
                else:
                    output += " / "
        output = output.replace("<", "&lt;")
        output = output.replace(">", "&gt;")
        output = output.replace("-", "")
        return output

    def convert_sentence(self, text):
        if text == '* **':
            return '<high-lulani>* **</high-lulani>'.format(text)
        output = '<high-lulani>.{0}.</high-lulani>'.format(self.convert_text(text))
        return output

    def convert_word(self, text):
        output = '<high-lulani>{0}</high-lulani>'.format(self.convert_text(text))
        return output


class VulgarLulani(HighLulani):
    def __init__(self):
        self.name = 'Vulgar Lulani'


class EarlyFezhle(English):
    def __init__(self):
        self.name = u'Early Fezhl\u00ea'
        self.safename = 'Early Fezhl&ecirc;'
        self.urlname = 'earlyfezhl()e'


class LateFezhle(English):
    def __init__(self):
        self.name = u'Late Fezhl\u00ea'
        self.safename = 'Late Fezhl&ecirc;'
        self.urlname = 'latefezhl()e'


class KoineFezhle(English):
    def __init__(self):
        self.name = u'Koine Fezhl\u00ea'
        self.safename = 'Koine Fezhl&ecirc;'
        self.urlname = 'koinefezhl()e'


class OldPtokan(English):
    def __init__(self):
        self.name = u'Old Ptokan'


class MiddlePtokan(English):
    def __init__(self):
        self.name = u'Middle Ptokan'


class StandardPtokan(English):
    def __init__(self):
        self.name = u'Standard Ptokan'


class PreBrequen(English):
    def __init__(self):
        self.name = u'Pre-Brequ\u00e8n'
        self.safename = 'Pre-Brequ&egrave;n'
        self.urlname = 'pre-brequ)en'


class ArchaicBrequen(English):
    def __init__(self):
        self.name = u'Archaic Brequ\u00e8n'
        self.safename = 'Archaic Brequ&egrave;n'
        self.urlname = 'archaicbrequ)en'


class CommonBrequen(English):
    def __init__(self):
        self.name = u'Common Brequ\u00e8n'
        self.safename = 'Common Brequ&egrave;n'
        self.urlname = 'commonbrequ)en'


class ProtoZhaladi(English):
    def __init__(self):
        self.name = u'Proto-Zhaladi'


class ContemporaryZhaladi(English):
    def __init__(self):
        self.name = u'Contemporary Zhaladi'


class ReformedZhaladi(English):
    def __init__(self):
        self.name = u'Reformed Zhaladi'


class ClassicalTsarin(English):
    def __init__(self):
        self.name = u'Classical Tsarin'


class ModernTsarin(English):
    def __init__(self):
        self.name = u'Modern Tsarin'


class AncientSolajin(English):
    def __init__(self):
        self.name = u'Ancient Solajin'


class MedievalSolajin(English):
    def __init__(self):
        self.name = u'Medieval Solajin'


class TraditionalSolajin(English):
    def __init__(self):
        self.name = u'Traditional Solajin'


class NewSolajin(English):
    def __init__(self):
        self.name = u'New Solajin'
