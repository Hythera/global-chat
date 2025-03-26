from discord.ext import commands, tasks
from discord import File, Embed
from datetime import datetime
from json import load

from database.models import Mutes
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)

class database_loop(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.check_mutes.start()

    @tasks.loop(minutes=10)
    async def check_mutes(self):
        try:
            mutes = await Mutes(None).list()
        except Exception as e:
            if e.args and e.args[0] != 2003:
                error_channel = self.client.get_channel(config["channels"]["errors"])
                line_image = File("images/line.png")
                log_embed = Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.title"),
                    description=translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.description", type="database_loop", command="None", user="`None`"),
                    color=0xED4245)
                log_embed.set_image(url="attachment://line.png")
                content_embed = Embed(
                    title=f"{config["emojis"]["file_text_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.content_embed.title"),
                    description=f"```{e}```",
                    color=0xED4245)
                content_embed.set_image(url="attachment://line.png")
                await error_channel.send(embeds=[log_embed, content_embed], files=[line_image])
                return
        for entry in mutes:
            if datetime.now() >= entry["expires_at"]:
                user = await Mutes(entry["user_id"]).load()
                if user.stored:
                    await user.remove()

    @check_mutes.before_loop
    async def before_update_stats(self):
        await self.client.wait_until_ready()

async def setup(client:commands.Bot) -> None:
    await client.add_cog(database_loop(client))