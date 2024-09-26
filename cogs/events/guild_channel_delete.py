import discord
from discord.ext import commands

from database.models import GlobalChannel

class guild_channel_delete(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener("on_guild_channel_delete")
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        try:
            if isinstance(channel, discord.TextChannel):
                global_channel = await GlobalChannel(channel_id=channel.id).load()
                if global_channel.stored == True:
                    await global_channel.remove()
        except Exception as e:
            print("on_guild_channel_delete: ", e)
            
async def setup(client:commands.Bot) -> None:
    await client.add_cog(guild_channel_delete(client))