import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import time

from database.models import UserRole, GlobalMessage
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

class report_message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.report_message_menu = app_commands.ContextMenu(name=discord.app_commands.locale_str("report_message"), callback=self.report_message_callback,)
        self.client.tree.add_command(self.report_message_menu) 

    @app_commands.checks.cooldown(1, 300, key=lambda i: i.user.id)
    async def report_message_callback(self, interaction: discord.Interaction, message: discord.Message):
        uuid = await GlobalMessage().get_uuid(message.id)
        if uuid:
            success_embed= discord.Embed(
                title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "menu.report_message.success_embed.title"),
                description=translator.translate(interaction.locale.value, "menu.report_message.success_embed.description"),
                color=0x57F287)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)

            message_author_id = int(message.embeds[0].author.url.split("/")[-1])
            message_content = message.embeds[0].description.replace('⠀', '')
            report_channel = self.client.get_channel(config["channels"]["reports"])

            line_image = discord.File("images/line.png")
            log_embed = discord.Embed(
                title=f"{config["emojis"]["alert_yellow"]} "+translator.translate(report_channel.guild.preferred_locale.value, "log.reports.log_embed.title"),
                description=translator.translate(report_channel.guild.preferred_locale.value, "log.reports.log_embed.description", reported_by=interaction.user.id, message_author=message_author_id, message_id=message.id, message_uuid=uuid),
                color=0xFEE75C)
            log_embed.set_image(url="attachment://line.png")
            content_embed = discord.Embed(
                description=f"```{message_content}```",
                color=0xFEE75C)
            content_embed.set_image(url="attachment://line.png")
            await report_channel.send(embeds=[log_embed, content_embed], files=[line_image])

        else:
            database_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.report_message.database_error_embed.title"),
                description=translator.translate(interaction.locale.value, "menu.report_message.database_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=database_error_embed, ephemeral=True)


async def setup(client:commands.Bot) -> None:
    await client.add_cog(report_message(client))