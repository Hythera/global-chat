import os
from dotenv import load_dotenv
from json import load
from pathlib import Path
import aiofiles
from aiomysql import Pool
from aiomysql import Warning as MySQLWarning 
import warnings
import asyncio
import time
from logging import WARN

import discord
from discord.ext import commands
from discord import app_commands

import pytz
from datetime import datetime
from colorama import Fore, Back, Style
import platform

from database import get_pool
from languages import CommandTranslator, Translator
translator = Translator()

load_dotenv()
with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)

async def init_db():
    pool: Pool = await get_pool()
    async with aiofiles.open('database/structure.sql') as file:
        sql = await file.read()
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            for statement in sql.split(';'):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", MySQLWarning) 
                        await cursor.execute(statement)
                except Exception as e:
                    print(e)
    pool.close()
    await pool.wait_closed()

async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        cooldown_error_embed = discord.Embed(
            title=f"{config["emojis"]["clock_red"]} "+translator.translate(interaction.locale.value, "on_tree_error.cooldown_error_embed.title"),
            description=translator.translate(interaction.locale.value, "on_tree_error.cooldown_error_embed.description", time=round(time.time()+error.retry_after)),  
            color=0xED4245)
        await interaction.response.send_message(embed=cooldown_error_embed, ephemeral=True)
    else:
        error_channel = client.get_channel(config["channels"]["errors"])
        line_image = discord.File("images/line.png")
        log_embed = discord.Embed(
            title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.title"),
            description=translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.description", type="interaction_tree_error", command=interaction.command.name, user=f"<@{interaction.user.id}>"),
            color=0xED4245)
        log_embed.set_image(url="attachment://line.png")
        content_embed = discord.Embed(
            title=f"{config["emojis"]["file_text_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.content_embed.title"),
            description=f"```{error}```",
            color=0xED4245)
        content_embed.set_image(url="attachment://line.png")
        await error_channel.send(embeds=[log_embed, content_embed], files=[line_image])

class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='/disabled', intents=intents, help_command=None)

        asyncio.run(init_db())
        self.cogslist = ['.'.join(file.relative_to('cogs').with_suffix('').parts) for file in Path('cogs').rglob('*.py') if not file.name.startswith('__')]
        self.tree.on_error = on_tree_error
        self.start_time = int(time.time())

    async def setup_hook(self):
        for cog in self.cogslist:
            await self.load_extension("cogs."+cog)

    async def on_ready(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        prfx = (Back.BLACK + Fore.CYAN + datetime.now(pytz.timezone('Europe/Berlin')).strftime("%H:%M:%S") + Back.RESET + Fore.WHITE + Style.NORMAL)
        print(prfx + " Logged in as " + Fore.BLUE + self.user.name)
        print(prfx + " Bot ID " + Fore.BLUE + str(self.user.id))
        print(prfx + " Discord Version " + Fore.BLUE+ discord.__version__)
        print(prfx + " Python Version " + Fore.BLUE + str(platform.python_version()))
        print (prfx + " Cogs Loaded " + Fore.BLUE + str(len(self.cogslist)))
        await self.tree.set_translator(CommandTranslator())
        global_commands = await self.tree.sync()
        guild_commands = await self.tree.sync(guild=discord.Object(id=config["admin_guild_id"]))
        print(prfx + " Slash CMDs Synced " + Fore.BLUE + str(len(guild_commands)+len(global_commands)) + " Commands")
        print("")
        await client.change_presence(activity = discord.CustomActivity(name=config["custom_app_status"]))

if __name__ == "__main__":
    client = Client()
    client.run(os.getenv('TOKEN'), log_level=WARN)