# custom-discord-bots
Various python discord bots used for my own server's, open-sourced and free to use.

## Techstack

![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=plastic&logo=docker&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-FCC624?style=plastic&logo=linux&logoColor=black) ![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=plastic&logo=discord&logoColor=white) ![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=plastic&logo=visual-studio-code&logoColor=white)

## Setup level bot
Create a .env file and copy this code with your corresponding values:

```
DISCORD_TOKEN=YOUR_DISCORD_TOKEN
LEVEL_CHANNEL_ID=YOUR_LEVEL_CHANNEL_ID
GUILD_ID=YOUR_SERVER_ID
```

## Setup reaction-role bot
1. Create message with reaction role information
2. Create emoji with same names as roles
3. Insert names into list `role_names` in `reaction-role/main.py`
4. Create a .env file and copy this code with your corresponding values:

```
DISCORD_TOKEN=YOUR_DISCORD_TOKEN
REACTION_ROLE_MESSAGE_ID=YOUR_REACTION_ROLE_MESSAGE_ID
```