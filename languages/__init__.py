import json
from string import Template
import os
from discord import Locale
from discord.app_commands import locale_str, TranslationContext
import discord

class Translator():
    def __init__(self):
        self.data = {}
        for filename in os.listdir("languages"):
            if filename.endswith(".json"):
                file_path = os.path.join("languages", filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.data[filename[:-5]] = json.load(file)

    def translate(self, lang: str, key: str, **kwargs) -> str:
        if lang not in self.data:
            lang = "en-US"
        if key not in self.data[lang]:
            print(f"Missing key ({lang}): {key}")
            return key
        text = self.data[lang][key]
        return Template(text).safe_substitute(**kwargs)
    
class CommandTranslator(discord.app_commands.Translator):
    async def load(self):
        pass

    async def unload(self):
        pass

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext):
        with open("languages/commands.json", 'r', encoding='utf-8') as file:
            translations = json.load(file)

        message_key = string.message  
        if locale.value in translations:
            return translations.get(locale.value, {}).get(message_key, None)
        else:
            return translations.get("en-US", {}).get(message_key, None)