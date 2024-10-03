import discord
from discord.ext import commands
from discord import app_commands
import json

from database.models import GlobalChannel, UserRole
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

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
    async def stats(self, interaction: discord.Interaction):
        global_channels_count = format_number(await GlobalChannel().len())
        user_count = format_number(await UserRole(None).len())
        guilds = format_number(len(self.client.guilds))
        users = format_number(len(self.client.users))
        ping = f"{round(self.client.latency * 1000)}ms"

        embed = discord.Embed(
            title=f"{config["emojis"]["bar_chart"]} "+translator.translate(interaction.locale.value, "command.stats.embed.title"),
            description=translator.translate(interaction.locale.value, "command.stats.embed.description", global_channels_count=global_channels_count, user_count=user_count, guilds=guilds, users=users, start_time=self.client.start_time, ping=ping),
        color=0x4e5058)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(stats_command(client))