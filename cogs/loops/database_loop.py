from discord.ext import commands, tasks
import datetime

from database.models import Mutes

class database_loop(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.check_mutes.start()

    @tasks.loop(minutes=10)
    async def check_mutes(self):
        mutes = await Mutes(None).list()
        for entry in mutes:
            if datetime.datetime.now() >= entry["expires_at"]:
                user = await Mutes(entry["user_id"]).load()
                if user.stored:
                    await user.remove()

    @check_mutes.before_loop
    async def before_update_stats(self):
        await self.client.wait_until_ready()

async def setup(client:commands.Bot) -> None:
    await client.add_cog(database_loop(client))