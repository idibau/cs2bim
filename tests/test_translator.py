from config.configuration import config as global_config
from i18n.language import Language
from i18n.translator import Translator


def test_translator_fallback_and_normalization(tmp_path):
    # Prepare minimal translation files
    de = tmp_path / "de.yml"
    fr = tmp_path / "fr.yml"
    it = tmp_path / "it.yml"
    de.write_text("greeting: Hallo\nworld: Welt")
    fr.write_text("greeting: Bonjour")
    it.write_text("")

    # Override global config paths
    global_config.i18n.de = de.as_posix()
    global_config.i18n.fr = fr.as_posix()
    global_config.i18n.it = it.as_posix()

    t = Translator()

    # Normalization: uppercase, punctuation, spaces -> key 'greeting'
    assert t.translate("Greeting!", Language.DE) == "Hallo"
    assert t.translate("Greeting!", Language.FR) == "Bonjour"

    # Missing key falls back to original segment
    assert t.translate("Unknown Key", Language.DE) == "Unknown Key"

    t = Translator()  # reload after file change
    assert t.translate("Greeting.World", Language.DE) == "Hallo.Welt"
