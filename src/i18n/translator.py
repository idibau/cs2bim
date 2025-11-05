import re
from pathlib import Path

from config.configuration import config
from i18n.language import Language
from utils.utils import load_yaml_as_flat_dict


class Translator:

    def __init__(self):
        self.de = self.load_translation_file(config.i18n.de) if config.i18n is not None else {}
        self.fr = self.load_translation_file(config.i18n.fr) if config.i18n is not None else {}
        self.it = self.load_translation_file(config.i18n.it) if config.i18n is not None else {}

    def translate(self, value: str, language: Language) -> str:
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
    def load_translation_file(path: str | None) -> dict[str, str]:
        if path is not None and Path(path).is_file():
           return load_yaml_as_flat_dict(path)
        else:
           return {}

    @staticmethod
    def get_translation_key(value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        value = re.sub(r"[^a-z0-9\s]", "", value)
        value = re.sub(r"\s+", "_", value.strip())
        return value
