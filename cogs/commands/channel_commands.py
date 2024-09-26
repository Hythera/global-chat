import discord
from discord.ext import commands
from discord import app_commands
import json

from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

class channel_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    channel_command = app_commands.Group(name=discord.app_commands.locale_str("command_channel"), description=discord.app_commands.locale_str("command_channel_description"), default_permissions=discord.Permissions(administrator=True), guild_only=True)

    @channel_command.command(name=discord.app_commands.locale_str("command_channel_set"), description=discord.app_commands.locale_str("command_channel_set_description"))
    @app_commands.describe(channel=discord.app_commands.locale_str("command_channel_set_describe_channel"))
    async def channel_set(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        await interaction.response.send_message(translator.translate(interaction.locale.value, "hello", user_id=interaction.user.id, username=interaction.user.name), ephemeral=True)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(channel_commands(client))