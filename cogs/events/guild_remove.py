import discord
from discord.ext import commands

from database.models import GlobalChannel

class guild_remove(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener("on_guild_remove")
    async def on_guild_remove(self, guild: discord.Guild):
        try:
            global_channel = await GlobalChannel(guild_id=guild.id).load()
            if global_channel.stored == True:
                await global_channel.remove()
        except Exception as e:
            print("on_guild_remove: ", e)
            
async def setup(client:commands.Bot) -> None:
    await client.add_cog(guild_remove(client))