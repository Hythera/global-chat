import os
from dotenv import load_dotenv
import json
from pathlib import Path
import aiofiles
from aiomysql import Pool
import asyncio

import discord
from discord.ext import commands

import pytz
from datetime import datetime
from colorama import Fore, Back, Style
import platform

from database import get_pool
from languages import CommandTranslator

load_dotenv()
with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

if not os.path.exists("json"):
    os.makedirs("json")

async def init_db():
    pool: Pool = await get_pool()
    async with aiofiles.open('database/structure.sql') as file:
        sql = await file.read()
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            for statement in sql.split(';'):
                try:
                    await cursor.execute(statement)
                except Exception as e:
                    continue
    pool.close()
    await pool.wait_closed()


class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='/disabled', intents=intents)

        asyncio.run(init_db())
        self.cogslist = ['.'.join(file.relative_to('cogs').with_suffix('').parts) for file in Path('cogs').rglob('*.py') if not file.name.startswith('__')]

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
        await client.change_presence(activity = discord.CustomActivity(name=config["custom_bot_status"]))

if __name__ == "__main__":
    client = Client()
    client.remove_command('help')
    client.run(os.getenv('TOKEN'))