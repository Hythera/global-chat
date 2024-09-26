from ast import Global
import discord
from discord.ext import commands
from discord import app_commands
import json

from database.models import GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

class channel_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    channel_command = app_commands.Group(name=discord.app_commands.locale_str("channel"), description=discord.app_commands.locale_str("channel_description"), default_permissions=discord.Permissions(administrator=True), guild_only=True)

    @channel_command.command(name=discord.app_commands.locale_str("channel_set"), description=discord.app_commands.locale_str("channel_set_description"))
    @app_commands.describe(channel=discord.app_commands.locale_str("channel_set_describe_channel"))
    @app_commands.rename(channel=discord.app_commands.locale_str("param_channel"))
    async def channel_set(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not channel:
            channel = interaction.channel
        global_channel = await GlobalChannel(channel.id, interaction.guild.id).load()
        if global_channel.stored == False:
            invite = str(await channel.create_invite())
            await global_channel.add(invite)
            await interaction.response.send_message("✅", ephemeral=True)
        else:
            await interaction.response.send_message("❌", ephemeral=True)
    
    @channel_command.command(name=discord.app_commands.locale_str("channel_remove"), description=discord.app_commands.locale_str("channel_remove_description"))
    async def channel_remove(self, interaction: discord.Interaction):
        global_channel = await GlobalChannel(guild_id=interaction.guild.id).load()
        if global_channel.stored == False:
            await interaction.response.send_message("❌", ephemeral=True)
        else:
            await global_channel.remove()
            await interaction.response.send_message("✅", ephemeral=True)
            
async def setup(client:commands.Bot) -> None:
    await client.add_cog(channel_commands(client))