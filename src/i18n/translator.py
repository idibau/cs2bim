import re
from pathlib import Path

from config.configuration import config
from i18n.language import Language
from utils.utils import load_yaml_as_flat_dict


class Translator:
    """
    Provides translation functionality for multiple languages.

    This class loads translation files for different languages (German, French, Italian)
    and provides methods to translate given texts based on normalized strings.
    """

    def __init__(self):
        self.de = self.load_translation_file(config.i18n.de) if config.i18n is not None else {}
        self.fr = self.load_translation_file(config.i18n.fr) if config.i18n is not None else {}
        self.it = self.load_translation_file(config.i18n.it) if config.i18n is not None else {}

    def translate(self, value: str, language: Language) -> str:
        """
        Translates the given string into the specified language.

        Args:
            value: The input string to be translated.
            language: The target language as a member of the `Language` enum.

        Returns:
            The translated string if available. If no translation is found or if no language is provided,
            returns the original input value.

        Raises:
            NotImplementedError: If the specified language is not supported.
        """
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
        """
        Loads a translation YAML file from the specified path as a flat dictionary.

        Args:
            path: The file path to the translation YAML file.

        Returns:
             A dictionary containing translation key-value pairs.
            Returns an empty dictionary if the path is None or does not exist.
        """
        if path is not None and Path(path).is_file():
            return load_yaml_as_flat_dict(path)
        else:
            return {}

    @staticmethod
    def get_translation_key(value: str | None) -> str | None:
        """
        Converts the provided string into a normalized translation key.

        Args:
            value: The input string to be used as a translation key.

        Returns:
            The resulting normalized key, or None if input is None.
        """
        if value is None:
            return None
        value = value.lower()
        value = re.sub(r"[^a-z0-9\s]", "", value)
        value = re.sub(r"\s+", "_", value.strip())
        return value
