import discord
from discord.ext import commands
from discord import app_commands
from json import load
import time
import asyncio

from database.models import UserRole, GlobalMessage, GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", "r", encoding="utf-8") as file:
    config = load(file)


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


class EmbedButtons(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, global_channel):
        super().__init__(timeout=None)
        server_invite = discord.ui.Button(label=translator.translate(interaction.locale.value, "menu.message_info.response_embed.button.server_invite"), style=discord.ButtonStyle.url, url=global_channel.invite)
        self.add_item(server_invite)


class message_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    message_command = app_commands.Group(name=discord.app_commands.locale_str("message"), description=discord.app_commands.locale_str("message_description"), default_permissions=discord.Permissions(manage_messages=True), guild_only=True, guild_ids=[config["admin_guild_id"]])

    @message_command.command(name=discord.app_commands.locale_str("delete"), description=discord.app_commands.locale_str("message_delete_description"))
    @app_commands.describe(uuid=discord.app_commands.locale_str("message_delete_describe_uuid"))
    async def message_delete(self, interaction: discord.Interaction, uuid: str):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 5:
            await interaction.response.defer(ephemeral=True)
            message_infos = await GlobalMessage().get_infos(uuid)
            global_messages = await GlobalMessage().get(uuid)
            
            if global_messages != []:
                instance_count = 0
                start_time = time.time() * 1000
                for global_message in global_messages:
                    channel = self.client.get_channel(global_message["channel_id"])
                    if channel:
                        try:
                            message = await channel.fetch_message(global_message["message_id"])
                            await message.delete()
                            instance_count += 1
                            await asyncio.sleep(0.05)  
                        except:
                            pass    
                duration = f"{int((time.time() * 1000) - start_time)}ms"
                success_embed= discord.Embed(
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.message_delete.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.message_delete.success_embed.description", count=instance_count, duration=duration),
                    color=0x57F287)
                await interaction.edit_original_response(embed=success_embed)

                message_author_id = message_infos[2]
                message_content = message.embeds[0].description.replace("⠀", "")
                staff_channel = self.client.get_channel(config["channels"]["actions"])

                line_image = discord.File("images/line.png")
                log_embed = discord.Embed(
                    title=f"{config["emojis"]["trash_red"]} "+translator.translate(staff_channel.guild.preferred_locale.value, "log.actions.delete_log_embed.title"),
                    description=translator.translate(staff_channel.guild.preferred_locale.value, "log.actions.delete_log_embed.description", deleted_by=interaction.user.id, message_author=message_author_id, uuid=uuid, instances=instance_count),
                    color=0xED4245)
                content_embed = discord.Embed(
                    title=f"{config["emojis"]["file_text_red"]} "+translator.translate(staff_channel.guild.preferred_locale.value, "log.actions.delete_log_content_embed.title"),
                    description=f"```\n{message_content}```",
                    color=0xED4245)
                content_embed.set_image(url="attachment://line.png")
                log_embed.set_image(url="attachment://line.png")

                await staff_channel.send(embeds=[log_embed, content_embed], files=[line_image])
            else:
                database_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.message_delete.database_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.message_delete.database_error_embed.description"),
                    color=0xED4245)
                await interaction.edit_original_response(embed=database_error_embed)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.role.set.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.role.set.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)

    @message_command.command(name=discord.app_commands.locale_str("information"), description=discord.app_commands.locale_str("message_information_description"))
    @app_commands.describe(uuid=discord.app_commands.locale_str("message_information_describe_uuid"))
    async def message_information(self, interaction: discord.Interaction, uuid: str):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 5:
            await interaction.response.defer(ephemeral=True)
            message_infos = await GlobalMessage().get_infos(uuid)
            global_messages = await GlobalMessage().get(uuid)
            
            if global_messages != []:
                try:
                    global_channel = await GlobalChannel(channel_id=message_infos[1]).load()
                    channel = self.client.get_channel(message_infos[1])
                except:
                    channel = None

                if channel:
                    response_embed = discord.Embed(
                        title=f"{config["emojis"]["file_text"]} "+translator.translate(interaction.locale.value, "menu.message_info.response_embed.title"),
                        description=translator.translate(interaction.locale.value, "menu.message_info.response_embed.description", user_id=message_infos[2], message_id=message_infos[0], message_uuid=uuid, instances=len(global_messages), guild_id=channel.guild.id, guild_name=channel.guild.name, guild_member_count=format_number(channel.guild.member_count), channel_id=channel.id, channel_name=channel.name),
                        color=0x4e5058)
                    await interaction.edit_original_response(embed=response_embed, view=EmbedButtons(interaction, global_channel))
                else:
                    message_error_embed = discord.Embed(
                        title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.message_info.message_error_embed.title"),
                        description=translator.translate(interaction.locale.value, "menu.message_info.message_error_embed.description"),
                        color=0xED4245)
                    await interaction.edit_original_response(embed=message_error_embed)
            else:
                database_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.message_delete.database_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.message_delete.database_error_embed.description"),
                    color=0xED4245)
                await interaction.edit_original_response(embed=database_error_embed)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.role.set.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.role.set.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)
      

async def setup(client:commands.Bot) -> None:
    await client.add_cog(message_commands(client))