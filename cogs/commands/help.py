import discord
from discord.ext import commands
from discord import app_commands
import json

from database.models import GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

class help_command(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name=discord.app_commands.locale_str("help"), description=discord.app_commands.locale_str("help_description"))
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        top_image = discord.File("images/banner/help_banner.png")
        top_embed = discord.Embed(color=0x4e5058)
        top_embed.set_image(url="attachment://help_banner.png")

        line_image = discord.File("images/line.png")
        embed = discord.Embed(
            title=f"{config["emojis"]["file_text"]} "+translator.translate(interaction.locale.value, "command.help.embed.title"),
            description=translator.translate(interaction.locale.value, "command.help.embed.description"),
            color=0x4e5058)
        embed.set_image(url="attachment://line.png")

        await interaction.edit_original_response(embeds=[top_embed, embed], attachments=[top_image, line_image], view=HelpButtons(interaction))

class HelpButtons(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)
        invite_app = discord.ui.Button(label=translator.translate(interaction.locale.value, "command.help.embed.button.invite_app"), style=discord.ButtonStyle.url, url=config["app_invite_url"])
        self.add_item(invite_app)
        support_server = discord.ui.Button(label=translator.translate(interaction.locale.value, "command.help.embed.button.support_server"), style=discord.ButtonStyle.url, url=config["support_server_url"])
        self.add_item(support_server)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(help_command(client))