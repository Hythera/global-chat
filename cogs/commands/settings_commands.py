import discord
from discord.ext import commands
from discord import app_commands
import json

from database.models import GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)


class settings_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    channel_command = app_commands.Group(name=discord.app_commands.locale_str("settings"), description=discord.app_commands.locale_str("settings_description"), default_permissions=discord.Permissions(administrator=True), guild_only=True)

    @channel_command.command(name=discord.app_commands.locale_str("invite"), description=discord.app_commands.locale_str("settings_invite_description"))
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    @app_commands.describe(status=discord.app_commands.locale_str("settings_invite_describe_status"))
    @app_commands.rename(status=discord.app_commands.locale_str("status"))
    @app_commands.choices(status=[app_commands.Choice(name=discord.app_commands.locale_str("choice_settings_invite_on"), value=1), 
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_settings_invite_off"), value=0)])
    async def setting_invite(self, interaction: discord.Interaction, status: app_commands.Choice[int]):
        global_channel = await GlobalChannel(guild_id=interaction.guild.id).load()
        if global_channel.stored == False:
            error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.settings.invite.channel_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.settings.invite.channe_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        else:
            if status.value == global_channel.setting_invite:
                if status.value == 0:
                    error_embed = discord.Embed(
                        title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.settings.invite.same_false_error_embed.title"),
                        description=translator.translate(interaction.locale.value, "command.settings.invite.same_false_embed.description"),
                        color=0xED4245)
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    error_embed = discord.Embed(
                        title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.settings.invite.same_true_error_embed.title"),
                        description=translator.translate(interaction.locale.value, "command.settings.invite.same_true_embed.description"),
                        color=0xED4245)
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await global_channel.update(setting_invite=status.value)
                if status.value == 1:
                    embed = discord.Embed(
                        title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.settings.invite.enabled_embed.title"),
                        description=translator.translate(interaction.locale.value, "command.settings.invite.enabled_embed.description"),
                        color=0x57F287)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.settings.invite.disabled_embed.title"),
                        description=translator.translate(interaction.locale.value, "command.settings.invite.disabled_embed.description"),
                        color=0x57F287)
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            
async def setup(client:commands.Bot) -> None:
    await client.add_cog(settings_commands(client))