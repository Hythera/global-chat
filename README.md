<p align="center"><img src="https://raw.githubusercontent.com/Blackstonecoden/global-chat/refs/heads/main/images/logo.png" alt="Global Chat Logo" width="200"></p>
<h1 align="center">Global Chat<br></h1>
<div align="center">
<a href="https://github.com/Blackstonecoden/global-chat"><img src="https://img.shields.io/github/stars/blackstonecoden/global-chat"></a>
<a href="https://discord.gg/FVQxgBysA7"><img src="https://img.shields.io/discord/1201557790758551574?color=5865f2&label=Discord&style=flat" alt="Discord"></a>
<br><br>
</div>

## 📌 Information
This is an open-source code for a Discord Global-Chat. It allows you to have a cross-server chat just by using this app. 
Key features:
- global-chat
- message deletion
- mute users
- custom roles
- localization (de/en)

## 🔌 Requirements
- [Python](https://www.python.org/)
- [MariDB](https://mariadb.org/) or [MySQL](https://www.mysql.com/)

## 🔧 Installation
Download the [latest release](https://github.com/Blackstonecoden/global-chat/releases/latest) from this repository. Setup the `.env` file in the root direcotry and fill it with your cridentials.
<details open>
  <summary style="font-size: 18px; cursor: pointer;">
    .env
  </summary>

```env
TOKEN = nGRuiORASD

database_host = 1.1.1.1:3306
database_user = user
database_password = password
database_name = s128_bot
```
</details>

Create the `config.json`. Here is the reference.
<details open>
  <summary style="font-size: 18px; cursor: pointer;">
    config.json
  </summary>

```json
{
    "admin_guild_id": 1234,
    "support_server_url": "https://discord.gg/1234",
    "app_invite_url": "https://example.com",

    "custom_app_status": "Hello, world!",

    "channels": {
        "reports": 1234,
        "errors": 1234,
        "actions": 1234
    },

    "roles": {
        "staff": {
            "permission_level": 0,
            "name": "Staff",
            "emoji": "<:staff:1234>",
            "color": "0x7289da"
        },
        "admin": {
            "permission_level": 10,
            "name": "Admin",
            "emoji": "<:admin:1234>",
            "color": "0x7289da"
        },
        "moderator": {
            "permission_level": 5,
            "name": "Moderator",
            "emoji": "<:moderator:1234>",
            "color": "0x7289da"
        },
        "partner": {
            "permission_level": 0,
            "name": "Partner",
            "emoji": "<:partner:1234>",
            "color": "0x7289da"
        },
        "verified": {
            "permission_level": 0,
            "name": "Verified",
            "emoji": "<:verified:1234>",
            "color": "0x7289da"
        },
        "default": {
            "permission_level": 0,
            "name": "Default",
            "display_name": "",
            "color": "0x4e5058"
        }
      },
    
    "emojis": {
        "x_circle_red":         "<:emoji:1234>",
        "clock_red":            "",
        "file_text_red":        "",
        "trash_red":            "",

        "alert_yellow":         "",
        "file_text_yellow":     "",

        "check_circle_green":   "",
        "plus_circle_green":    "",

        "users":                "",
        "file_text":            "",
        "bar_chart":            ""
    },
    "standard_server_icon_url": "https://discord.com/assets/ca24969f2fd7a9fb03d5.png"
}
```
</details>

## 📄 Notes

To assign yourself a role, you have two options:

1. Log into the database using a client like [MySQL Workbench](https://www.mysql.com/products/workbench/) and manually insert your user ID, role, and display role into the `user_roles` table.

2. Alternatively, temporarily add the following code in the `setup_hook` of the `Client` class in `main.py` and replace 1234 with your user ID:
   ```py
   from database.models import UserRole
   await UserRole(1234).change("admin")
    ```
Ensure that you have a permission level of at least 10 to use all commands.