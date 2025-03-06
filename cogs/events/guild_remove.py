from discord.ext import commands
from discord import File, Embed, Guild
from json import load

from database.models import GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)


class guild_remove(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener("on_guild_remove")
    async def on_guild_remove(self, guild: Guild):
        try:
            global_channel = await GlobalChannel(guild_id=guild.id).load()
            if global_channel.stored == True:
                await global_channel.remove()
        except Exception as e:
            if e[0] != 2003: 
                error_channel = self.client.get_channel(config["channels"]["errors"])
                line_image = File("images/line.png")
                log_embed = Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.title"),
                    description=translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.description", type="on_guild_remove", command="None", user="`None`"),
                    color=0xED4245)
                log_embed.set_image(url="attachment://line.png")
                content_embed = Embed(
                    title=f"{config["emojis"]["file_text_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.content_embed.title"),
                    description=f"```{e}```",
                    color=0xED4245)
                content_embed.set_image(url="attachment://line.png")
                await error_channel.send(embeds=[log_embed, content_embed], files=[line_image])
            
async def setup(client:commands.Bot) -> None:
    await client.add_cog(guild_remove(client))