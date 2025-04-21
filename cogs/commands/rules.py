import discord
from discord.ext import commands
from discord import app_commands
from json import load

from languages import Translator
translator = Translator()

with open("config.json", "r", encoding="utf-8") as file:
    config = load(file)

class rules_command(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name=discord.app_commands.locale_str("rules"), description=discord.app_commands.locale_str("rules_description"))
    async def rules(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        top_image = discord.File("images/banners/rules_banner.png")
        top_embed = discord.Embed(color=0x4e5058)
        top_embed.set_image(url="attachment://rules_banner.png")

        line_image = discord.File("images/line.png")
        embed = discord.Embed(
            title=f"{config["emojis"]["book"]} "+translator.translate(interaction.locale.value, "command.rules.embed.title"),
            description=translator.translate(interaction.locale.value, "command.rules.embed.description"),
            color=0x4e5058)
        embed.set_image(url="attachment://line.png")

        await interaction.edit_original_response(embeds=[top_embed, embed], attachments=[top_image, line_image], view=RulesButtons(interaction))

class RulesButtons(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)
        invite_app = discord.ui.Button(label=translator.translate(interaction.locale.value, "command.rules.embed.button.invite_app"), style=discord.ButtonStyle.url, url=config["app_invite_url"])
        self.add_item(invite_app)
        support_server = discord.ui.Button(label=translator.translate(interaction.locale.value, "command.rules.rules.button.support_server"), style=discord.ButtonStyle.url, url=config["support_server_url"])
        self.add_item(support_server)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(rules_command(client))