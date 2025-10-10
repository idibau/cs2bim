import re
from pathlib import Path

from i18n.language import Language
from utils.utils import load_yaml_as_flat_dict


class Translator:

    def __init__(self):
        self.de = self.load_translation_file("i18n/de.yml")
        self.fr = self.load_translation_file("i18n/fr.yml")
        self.it = self.load_translation_file("i18n/it.yml")

    def translate(self, value, language):
        if language is None:
            return value
        elif language == Language.DE:
            return self.de.get(self.get_translation_key(value), value)
        elif language == Language.FR:
            return self.fr.get(self.get_translation_key(value), value)
        elif language == Language.IT:
            return self.it.get(self.get_translation_key(value), value)
        else:
            raise NotImplementedError(f"No translation available for {language.name}")

    @staticmethod
    def load_translation_file(path):
        if Path(path).is_file():
           return load_yaml_as_flat_dict(path)
        else:
           return {}

    @staticmethod
    def get_translation_key(value):
        if value is None:
            return None
        value = value.lower()
        value = re.sub(r"[^a-z0-9\s]", "", value)
        value = re.sub(r"\s+", "_", value.strip())
        return value
