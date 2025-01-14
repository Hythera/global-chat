import discord
from discord.ext import commands
from discord import app_commands
from json import load
from datetime import timedelta, datetime

from database.models import UserRole, Mutes
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)

times = {
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "6h": timedelta(hours=6),
    "12h": timedelta(hours=12),
    "1d": timedelta(days=1),
    "7d": timedelta(days=7)
}

class mute_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    mute_command = app_commands.Group(name=discord.app_commands.locale_str("mute"), description=discord.app_commands.locale_str("mute_description"), default_permissions=discord.Permissions(administrator=True), guild_only=True, guild_ids=[config["admin_guild_id"]])

    @mute_command.command(name=discord.app_commands.locale_str("add"), description=discord.app_commands.locale_str("mute_add_description"))
    @app_commands.describe(user=discord.app_commands.locale_str("mute_add_describe_user"), time=discord.app_commands.locale_str("mute_add_describe_time"), reason=discord.app_commands.locale_str("mute_add_describe_reason"))
    @app_commands.rename(user=discord.app_commands.locale_str("user"), time=discord.app_commands.locale_str("time"), reason=discord.app_commands.locale_str("reason"))
    @app_commands.choices(time=[app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_15m"), value="15m"), 
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_1h"), value="1h"), 
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_6h"), value="6h"), 
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_12h"), value="12h"), 
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_1d"), value="1d"), 
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_7d"), value="7d"),
                                app_commands.Choice(name=discord.app_commands.locale_str("choice_mute_add_permanent"), value="permanent")])
    async def mute_add(self, interaction: discord.Interaction, user: discord.User, time: app_commands.Choice[str], reason: str):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 10:
            mute = await Mutes(user.id).load()
            if mute.stored:
                user_exists_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.mute.add.user_exists_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.mute.add.user_exists_error_embed.description"),
                    color=0xED4245)
                await interaction.response.send_message(embed=user_exists_error_embed, ephemeral=True)
            else:
                if time.value != "permanent":
                    expires_at = datetime.now() + times[time.value]
                    await mute.add(interaction.user.id, reason, expires_at.strftime('%Y-%m-%d %H:%M:%S'))
                    time_str = f"<t:{int(expires_at.timestamp())}:R>"
                else:
                    await mute.add(interaction.user.id, reason, None)   
                    time_str = translator.translate(interaction.locale.value, "command.mute.add.succes_embed.translation.never")
                    
                success_embed = discord.Embed(
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.mute.add.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.mute.add.success_embed.description", user_id=user.id, time=time_str, reason=reason, staff_id=interaction.user.id),
                    color=0x57F287)
                await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.mute.add.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.mute.add.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)


    @mute_command.command(name=discord.app_commands.locale_str("remove"), description=discord.app_commands.locale_str("mute_remove_description"))
    @app_commands.describe(user=discord.app_commands.locale_str("mute_remove_describe_user"))
    @app_commands.rename(user=discord.app_commands.locale_str("user"))
    async def mute_remove(self, interaction: discord.Interaction, user: discord.User):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 10:
            mute = await Mutes(user.id).load()
            if mute.stored:
                await mute.remove()
                success_embed = discord.Embed(
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.mute.remove.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.mute.remove.success_embed.description"),
                    color=0x57F287)
                await interaction.response.send_message(embed=success_embed, ephemeral=True)
            else:
                user_not_exists_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.mute.remove.user_not_exists_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.mute.remove.user_not_exists_error_embed.description"),
                    color=0xED4245)
                await interaction.response.send_message(embed=user_not_exists_error_embed, ephemeral=True)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.mute.remove.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.mute.remove.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)


async def setup(client:commands.Bot) -> None:
    await client.add_cog(mute_commands(client))