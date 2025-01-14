import discord
from discord.ext import commands
from discord import app_commands
from typing import Sequence
from json import load

from database.models import GlobalChannel, UserRole, GlobalMessage
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)

def get_users(guilds: Sequence[discord.Guild])-> int:
    users = 0
    for guild in guilds:
        users+= guild.member_count
    return users

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

class stats_command(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name=discord.app_commands.locale_str("stats"), description=discord.app_commands.locale_str("stats_description"))
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(config["admin_guild_id"])
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        global_messages_count = format_number(await GlobalMessage().len())
        global_channels_count = format_number(await GlobalChannel().len())
        user_count = format_number(await UserRole(None).len())
        guilds = format_number(len(self.client.guilds))
        users = format_number(get_users(self.client.guilds))
        ping = f"{round(self.client.latency * 1000)}ms"

        embed = discord.Embed(
            title=f"{config["emojis"]["bar_chart"]} "+translator.translate(interaction.locale.value, "command.stats.embed.title"),
            description=translator.translate(interaction.locale.value, "command.stats.embed.description", global_messages_count=global_messages_count, global_channels_count=global_channels_count, user_count=user_count, guilds=guilds, users=users, start_time=self.client.start_time, ping=ping),
        color=0x4e5058)

        await interaction.edit_original_response(embed=embed)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(stats_command(client))