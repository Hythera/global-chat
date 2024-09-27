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

    @channel_command.command(name=discord.app_commands.locale_str("set"), description=discord.app_commands.locale_str("channel_set_description"))
    @app_commands.describe(channel=discord.app_commands.locale_str("channel_set_describe_channel"))
    @app_commands.rename(channel=discord.app_commands.locale_str("channel"))
    async def channel_set(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not channel:
            channel = interaction.channel
        global_channel = await GlobalChannel(channel.id, interaction.guild.id).load()
        if global_channel.stored == False:
            invite = str(await channel.create_invite())
            await global_channel.add(invite)
            try:
                await channel.edit(slowmode_delay=5)
            except:
                pass

            success_embed = discord.Embed(
                title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.channel.set.success_embed.title"),
                description=translator.translate(interaction.locale.value, "command.channel.set.success_embed.description", channel_id=channel.id),
                color=0x57F287)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.channel.set.error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.channel.set.error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @channel_command.command(name=discord.app_commands.locale_str("remove"), description=discord.app_commands.locale_str("channel_remove_description"))
    async def channel_remove(self, interaction: discord.Interaction):
        global_channel = await GlobalChannel(guild_id=interaction.guild.id).load()
        if global_channel.stored == False:
            error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.channel.remove.error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.channel.remove.error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        else:
            await global_channel.remove()
            success_embed= discord.Embed(
                title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.channel.remove.success_embed.title"),
                description=translator.translate(interaction.locale.value, "command.channel.remove.success_embed.description"),
                color=0x57F287)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
async def setup(client:commands.Bot) -> None:
    await client.add_cog(channel_commands(client))