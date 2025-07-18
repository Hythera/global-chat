import discord
from discord.ext import commands
from discord import app_commands
from json import load

from database.models import UserRole
from languages import Translator
translator = Translator()

with open("config.json", "r", encoding="utf-8") as file:
    config = load(file)

role_choices = [app_commands.Choice(name=role_key, value=role_key) for role_key in config["roles"]]

class user_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    user_command = app_commands.Group(name=discord.app_commands.locale_str("user"), description=discord.app_commands.locale_str("user_description"), default_permissions=discord.Permissions(administrator=True), guild_only=True, guild_ids=[config["admin_guild_id"]])

    @user_command.command(name=discord.app_commands.locale_str("set"), description=discord.app_commands.locale_str("user_set_description"))
    @app_commands.describe(user=discord.app_commands.locale_str("user_set_describe_user"), role=discord.app_commands.locale_str("user_set_describe_role"), display_role=discord.app_commands.locale_str("user_set_describe_display_role"))
    @app_commands.rename(user=discord.app_commands.locale_str("user"), role=discord.app_commands.locale_str("role"), display_role=discord.app_commands.locale_str("display_role"))
    @app_commands.choices(role=role_choices, display_role=role_choices)
    async def user_set(self, interaction: discord.Interaction, user: discord.User, role: app_commands.Choice[str], display_role: app_commands.Choice[str] = None):
        if not display_role:
            display_role = role
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 10:
            target = await UserRole(user.id).load()
            if role.value == "default":
                if target.stored:
                    await target.remove()
                    success_removed_embed = discord.Embed(
                        title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.user.set.success_removed_embed.title"),
                        description=translator.translate(interaction.locale.value, "command.user.set.success_removed_embed.description", user_id=user.id, role=role.value),
                        color=0x57F287)
                    await interaction.response.send_message(embed=success_removed_embed, ephemeral=True)
                else:
                    user_is_default_error_embed = discord.Embed(
                        title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.user.set.user_is_default_error_embed.title"),
                        description=translator.translate(interaction.locale.value, "command.user.set.user_is_default_error_embed.description"),
                        color=0xED4245)
                    await interaction.response.send_message(embed=user_is_default_error_embed, ephemeral=True)
            elif target.stored and (target.role == role.value and target.display_role == display_role.value):
                same_role_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.user.set.same_role_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.user.set.same_role_error_embed.description"),
                    color=0xED4245)
                await interaction.response.send_message(embed=same_role_error_embed, ephemeral=True)
            else:
                await target.change(role.value, display_role.value)
                success_embed = discord.Embed(
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.user.set.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.user.set.success_embed.description", user_id=user.id, role=role.value, display_role=display_role.value),
                    color=0x57F287)
                await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.user.set.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.user.set.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)

    @user_command.command(name=discord.app_commands.locale_str("list"), description=discord.app_commands.locale_str("user_list_description"))
    async def user_list(self, interaction: discord.Interaction):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 10:
            users = await author.list()

            staff_dict = {role: [] for role in config["roles"] if role != "default"}
            for user in users:
                if user["role"] == user["display_role"]:
                    staff_dict[user["role"]].append(f"> - <@{user["user_id"]}>")
                else:
                    staff_dict[user["role"]].append(f"> - <@{user["user_id"]}> - `{user["display_role"]}`")
            formatted_text = ""
            roles = [role for role, members in staff_dict.items() if members]
            for i, role in enumerate(roles):
                members = staff_dict[role]
                if members:
                    formatted_text += f"\n> {config["roles"][role]["emoji"]} **{config["roles"][role]["name"]} - {len(members)}**\n"
                    formatted_text += "\n ".join(members)
                    if i < sum(1 for users in staff_dict.values() if users)-1:
                        formatted_text += "\n > "

            embed = discord.Embed(
                title=f"{config["emojis"]["users"]} "+translator.translate(interaction.locale.value, "command.user.list.embed.title"),
                description=translator.translate(interaction.locale.value, "command.user.list.embed.description")+formatted_text,
                color=0x4e5058)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.user.list.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.user.list.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)
        

async def setup(client:commands.Bot) -> None:
    await client.add_cog(user_commands(client))