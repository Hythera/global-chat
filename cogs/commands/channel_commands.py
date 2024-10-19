import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import string
import random

from database.models import GlobalChannel, GlobalMessage
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

def generate_random_string():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(20))
    return random_string

def format_number(number: int) -> str:
    if number >= 10_000_000:
        return f"{number // 1_000_000}M" 
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 10_000:
        return f"{number // 1_000}k" 
    elif number >= 1000:
        return f"{number / 1000:.1f}k"
    else:
        return number

class channel_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    channel_command = app_commands.Group(name=discord.app_commands.locale_str("channel"), description=discord.app_commands.locale_str("channel_description"), default_permissions=discord.Permissions(administrator=True), guild_only=True)

    @channel_command.command(name=discord.app_commands.locale_str("set"), description=discord.app_commands.locale_str("channel_set_description"))
    @app_commands.checks.cooldown(1, 300, key=lambda i: i.user.id)
    @app_commands.describe(channel=discord.app_commands.locale_str("channel_set_describe_channel"))
    @app_commands.rename(channel=discord.app_commands.locale_str("channel"))
    async def channel_set(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not channel:
            channel = interaction.channel
        global_channel = await GlobalChannel(channel.id, interaction.guild.id).load()
        if global_channel.stored == False:
            try:
                invite = str(await channel.create_invite())
                await global_channel.add(invite)
            except:
                await global_channel.add(config["support_server_url"])
            try:
                await channel.edit(slowmode_delay=5)
            except:
                pass

            success_embed = discord.Embed(
                title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.channel.set.success_embed.title"),
                description=translator.translate(interaction.locale.value, "command.channel.set.success_embed.description", channel_id=channel.id),
                color=0x57F287)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)

            uuid = generate_random_string()
            channels = await GlobalChannel().get_all_channels()
            for entry in channels:
                if entry["guild_id"] != channel.guild.id:
                    loop_channel: discord.TextChannel = self.client.get_channel(entry["channel_id"])
                    if loop_channel:
                        try:
                            perms: discord.Permissions = loop_channel.permissions_for(loop_channel.guild.get_member(self.client.user.id))
                            if perms.send_messages:
                                global_embed = discord.Embed(
                                    title=f"{config["emojis"]["plus_circle_green"]} "+translator.translate(loop_channel.guild.preferred_locale.value, "command.channel.set.global_embed.title"),
                                    description=translator.translate(loop_channel.guild.preferred_locale.value, "command.channel.set.global_embed.description", guild=channel.guild.name, users=format_number(channel.guild.member_count)),
                                    color=0x57F287)
                                if channel.guild.icon:
                                    global_embed.set_thumbnail(url=channel.guild.icon.with_size(256).url)
                                    
                                sent_message = await loop_channel.send(embed=global_embed)
                                await GlobalMessage().add(uuid, sent_message.id, sent_message.channel.id)
                                await asyncio.sleep(0.05)
                        except:
                            pass
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