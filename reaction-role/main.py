import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

role_names = [
    "valorant",
    "league_of_legends",
    "marvel_rivals",
    "pokemon_tcg_pocket",
    "counter_strike_2",
    "overwatch_2",
    "strinova",
    "fortnite",
    "honkai_star_rail",
    "zenless_zone_zero",
    "minecraft",
    "monster_hunter_wilds",
]

REACTION_ROLE_MESSAGE_ID: int = int(os.getenv("REACTION_ROLE_MESSAGE_ID"))
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_raw_reaction_add(self, payload):
        if payload.message_id == REACTION_ROLE_MESSAGE_ID:
            if (role_name := payload.emoji.name) in role_names:
                guild = client.get_guild(int(payload.guild_id))
                role = discord.utils.get(guild.roles, name=role_name)
                await payload.member.add_roles(role)

    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == REACTION_ROLE_MESSAGE_ID:
            if (role_name := payload.emoji.name) in role_names:
                guild = client.get_guild(int(payload.guild_id))
                role = discord.utils.get(guild.roles, name=role_name)
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.remove_roles(role)


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
client = Client(command_prefix="!", intents=intents)

client.run(DISCORD_TOKEN)
