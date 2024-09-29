<p align="center"><img src="https://raw.githubusercontent.com/Blackstonecoden/global-chat/refs/heads/main/images/logo.png" alt="Global Chat Logo" width="200"></p>
<h1 align="center">Global Chat<br>
	<a href="https://github.com/Blackstonecoden/global-chat"><img src="https://img.shields.io/github/stars/blackstonecoden/global-chat"></a>
	<a href="https://discord.gg/FVQxgBysA7"><img src="https://img.shields.io/discord/1201557790758551574?color=5865f2&label=Discord&style=flat" alt="Discord"></a>
	<br><br>
</h1>

## 📌 Information
This is an open-source code for a Discord Global-Chat. It allows you to have a cross-server chat just by using this app. 
Key features:
- Global-Chat
- message deletion
- mute users
- custom roles

## 🔌 Requirements
- [Python](https://www.python.org/)
- [MariDB](https://mariadb.org/) or [MySQL](https://www.mysql.com/)

## 🔧 Installation
Download the [latest release](https://github.com/Blackstonecoden/global-chat/releases/latest) from this repository. Setup the `.env` file in the root direcotry and fill it with your cridentials.
```env
TOKEN = nGRuiORASD

database_host = 1.1.1.1:3306
database_user = user
database_password = password
database_name = s128_bot
```
Create the `config.json`.
```json
{
    "admin_guild_id": 123,
    "support_server_url": "https://discord.gg/123",
    "app_invite_url": "https://example.com",

    "custom_app_status": "Hello, world!",

    "channels": {
        "reports": 123
    },

    "roles": {
        "developer": {
            "permission_level": 20,
            "name": "Developer",
            "display_name": "<:developer:123> DEV",
            "color": "0x5865f2"
        },
        "admin": {
            "permission_level": 10,
            "name": "Admin",
            "display_name": "<:admin:123> Admin",
            "color": "0xf54651"
        },
        "moderator": {
            "permission_level": 5,
            "name": "Moderator",
            "display_name": "<:moderator:123> MOD",
            "color": "0xfc964b"
        },
        "partner": {
            "permission_level": 0,
            "name": "Partner",
            "display_name": "<:partner:123> Partner",
            "color": "0x4dbc62"
        },
        "vip": {
            "permission_level": 0,
            "name": "VIP",
            "display_name": "<:vip:123> VIP",
            "color": "0xfbb848"
        },
        "default": {
            "permission_level": 0,
            "name": "Default",
            "display_name": "",
            "color": "0x4e5058"
        }
      },
    
    "emojis": {
        "x_circle_red": "<:emoji:1234>",
        "clock_red": "",

        "alert_yellow": "",
        "check_circle_green": "",

        "users": "",
        "file_text": ""
    },
    "standard_server_icon_url": "https://discord.com/assets/ca24969f2fd7a9fb03d5.png"
}
```