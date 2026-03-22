from abc import ABC, abstractmethod
import argostranslate.package as argospkg
import argostranslate.translate as argosmt


class AbstractTranslator(ABC):

    @abstractmethod
    def translate(self, input: str, src_lang: str, target_lang: str) -> str:
        ...


class SimpleArgosTranslator(AbstractTranslator):

    def __init__(self, src_lang: str, target_lang: str):
        print(f"Initializing translator for {src_lang} -> {target_lang}")
        self.src_lang = src_lang
        self.target_lang = target_lang
        argospkg.update_package_index()
        available_packages = argospkg.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == self.src_lang and x.to_code == self.target_lang, available_packages
            )
        )
        argospkg.install_from_path(package_to_install.download())

    def translate(self, input: str, src_lang: str, target_lang: str) -> str:
        print(f"Translating from {src_lang} to {target_lang}: {input}")
        result = argosmt.translate(input, src_lang, target_lang)
        print(f"Result: {result}")
        return result
