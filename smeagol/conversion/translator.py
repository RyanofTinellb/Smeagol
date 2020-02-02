# -*- coding: utf-8 -*-
import re


class Translator:
    def __init__(self, language=None):
        language = language or 'en'
        languages = dict(
            en=English,
            hl=HighLulani,
            dl=DemoticLulani,
            ef=EarlyFezhle,
            lf=LateFezhle,
            kf=KoineFezhle,
            op=OldPtokan,
            mp=MiddlePtokan,
            sp=StandardPtokan,
            pb=PreBrequen,
            ab=ArchaicBrequen,
            cb=CommonBrequen,
            pz=ProtoZhaladi,
            cz=ContemporaryZhaladi,
            rz=ReformedZhaladi,
            ct=ClassicalTsarin,
            mt=ModernTsarin)
        languages.update({'as': AncientSolajin})
        languages.update(dict(
            ms=MedievalSolajin,
            ts=TraditionalSolajin,
            ns=NewSolajin))
        self.number = len(languages)
        self.languages = languages
        self.select(language)
        
    def _iter_(self):
        return iter(self.languages)
        
    def select(self, language):
        language = language.lower()[:2]
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

    @property
    def fullname(self):
        return f'{self.code}: {self.name}'

    def encode(self, languagename):
        languagename = languagename.lower()
        for code, language in self.languages.items():
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

    def convert(self, text, kind='text'):
        convert = getattr(self.converter, f'convert_{kind}')
        tag = getattr(self.converter, 'tag')
        return '<{0}>{1}</{0}>'.format(tag, convert(text))

    def convert_text(self, text):
        return self.convert(text)

    def convert_word(self, text):
        return self.convert(text, 'word')

    def convert_sentence(self, text):
        return self.convert(text, 'sentence')


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
        self.tag = 'high-lulani'

    # Converts a transliterated text into High Lulani text
    # See grammar.tinellb.com/highlulani for details.
    @staticmethod
    def convert_text(text):
        if text == '***':
            return text

        # removes full stops if before a parenthesis
        text = text.replace('.(', '(')

        # removes markdown tags, hyphens, dollars, parentheses and quote marks
        text = re.sub("\[(|/)[a-z]\]|-|[$()]|'\\\"|\\\"", "", text)

        # removes angle brackets and information between them
        text = re.sub(r'<.*?>', '', text)

        # replaces "upper case" glottal stop with "lower case" apostrophe
        text = re.sub('(“| |^)ʔ', r'\1’', text)
        text = text.lower()
        output = ''
        for last, this in zip(text, text[1:]):
            if this == last:
                output += ";"
            elif last == "-":
                if this in "aiu":
                    output += "/" + this
            elif last == '’':
                output += this
            elif this == "a":
                output += last
            elif this == "i":
                output += last.upper()
            elif this == "u":
                index = "pbtdcjkgmnqlrfsxh".find(last)
                output += "oOeEyY$%UIAWwvzZV"[index]
            elif this == " ":
                if last in ".!?":
                    output += " . "
                elif last in ",;:":
                    output += " , "
                else:
                    output += " / "
        output = output.replace("-", "")
        return output

    def convert_sentence(self, text):
        if text == '***':
            return '***'
        output = f'.{self.convert_text(text)}.'
        return output

    def convert_word(self, text):
        output = f'{self.convert_text(text)}'
        return output


class DemoticLulani(HighLulani):
    def __init__(self):
        self.name = 'Demotic Lulani'


class EarlyFezhle(English):
    def __init__(self):
        self.name = 'Early Fezhl\u00ea'
        self.safename = 'Early Fezhl&ecirc;'
        self.urlname = 'earlyfezhl()e'


class LateFezhle(English):
    def __init__(self):
        self.name = 'Late Fezhl\u00ea'
        self.safename = 'Late Fezhl&ecirc;'
        self.urlname = 'latefezhl()e'


class KoineFezhle(English):
    def __init__(self):
        self.name = 'Koine Fezhl\u00ea'
        self.safename = 'Koine Fezhl&ecirc;'
        self.urlname = 'koinefezhl()e'


class OldPtokan(English):
    def __init__(self):
        self.name = 'Old Ptokan'


class MiddlePtokan(English):
    def __init__(self):
        self.name = 'Middle Ptokan'


class StandardPtokan(English):
    def __init__(self):
        self.name = 'Standard Ptokan'


class PreBrequen(English):
    def __init__(self):
        self.name = 'Pre-Brequ\u00e8n'
        self.safename = 'Pre-Brequ&egrave;n'
        self.urlname = 'pre-brequ)en'


class ArchaicBrequen(English):
    def __init__(self):
        self.name = 'Archaic Brequ\u00e8n'
        self.safename = 'Archaic Brequ&egrave;n'
        self.urlname = 'archaicbrequ)en'


class CommonBrequen(English):
    def __init__(self):
        self.name = 'Common Brequ\u00e8n'
        self.safename = 'Common Brequ&egrave;n'
        self.urlname = 'commonbrequ)en'


class ProtoZhaladi(English):
    def __init__(self):
        self.name = 'Proto-Zhaladi'


class ContemporaryZhaladi(English):
    def __init__(self):
        self.name = 'Contemporary Zhaladi'


class ReformedZhaladi(English):
    def __init__(self):
        self.name = 'Reformed Zhaladi'


class ClassicalTsarin(English):
    def __init__(self):
        self.name = 'Classical Tsarin'


class ModernTsarin(English):
    def __init__(self):
        self.name = 'Modern Tsarin'


class AncientSolajin(English):
    def __init__(self):
        self.name = 'Ancient Solajin'


class MedievalSolajin(English):
    def __init__(self):
        self.name = 'Medieval Solajin'


class TraditionalSolajin(English):
    def __init__(self):
        self.name = 'Traditional Solajin'


class NewSolajin(English):
    def __init__(self):
        self.name = 'New Solajin'
