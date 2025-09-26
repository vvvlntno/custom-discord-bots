import json
import logging
import os
import time
from typing import List

import discord
from discord.ext import commands
from dotenv import load_dotenv

from models import xp_to_level_dict

logging.basicConfig(level=logging.INFO)
load_dotenv()

JSON_FILE_PATH_USERS_LEVEL_DATA = r"./users_level_data.json"
JSON_FILE_PATH_USERS_VOICE_CHANNEL_DATA = r"./users_voice_channel_data.json"
LEVEL_CHANNEL_ID: int = int(os.getenv("LEVEL_CHANNEL_ID"))
GUILD_ID: int = int(os.getenv("GUILD_ID"))
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")

print(GUILD_ID, LEVEL_CHANNEL_ID, DISCORD_TOKEN)


def experience_points_to_level(experience_points: int) -> int:
    level = 1
    for xp_threshold, lvl in sorted(xp_to_level_dict.items()):
        if experience_points >= xp_threshold:
            level = lvl
        else:
            break
    return level


def get_role_name_based_on_level(user_data: List[dict], msg_author_id: str) -> str:
    role_name = ""
    for user in user_data:
        if user["author_id"] == msg_author_id:
            if user["level"] < 10:
                role_name = "level_1"
            elif user["level"] < 25:
                role_name = "level_10"
            elif user["level"] < 50:
                role_name = "level_25"
            elif user["level"] < 70:
                role_name = "level_50"
            elif user["level"] < 80:
                role_name = "level_70"
            elif user["level"] < 90:
                role_name = "level_80"
            elif user["level"] < 100:
                role_name = "level_90"
            elif user["level"] >= 100:
                role_name = "level_100"
    return role_name


def read_json_data(json_file: str) -> str:
    with open(json_file, "r") as f:
        return json.load(f)


def write_json_data(json_file: str, user_data: str) -> str:
    with open(json_file, "w") as f:
        json.dump(user_data, f, indent=2)


async def add_experience_points_to_user(
    json_file_name: str, member: discord.member.Member, experience_point_amount: int
) -> None:
    # load data
    user_data = read_json_data(json_file=json_file_name)

    # check if user exists and add xp
    match = False
    for user in user_data:
        if user["author_id"] == str(member.id):
            user["experience_points"] += experience_point_amount
            new_level = experience_points_to_level(user["experience_points"])
            # set new level if required
            if new_level != user["level"]:
                user["level"] = new_level
                channel = client.get_channel(LEVEL_CHANNEL_ID)
                await channel.send(
                    f"Congrats {member.mention} you achieved level {new_level}"
                )
            match = True

    # create new user if not exists
    if not match:
        level = experience_points_to_level(experience_points=experience_point_amount)
        new_user = {
            "author_id": str(member.id),
            "experience_points": experience_point_amount,
            "level": level,
            "user_name": member.name,
        }
        user_data.append(new_user)
        logging.info("Created new user %s and added to the database", member.name)

    # add data back to database
    write_json_data(json_file=json_file_name, user_data=user_data)

    # give role based on level
    role_name = get_role_name_based_on_level(
        user_data=user_data, msg_author_id=str(member.id)
    )
    guild = client.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name=role_name)
    await member.add_roles(role)


def add_new_user_entry_into_voice_channel_data(
    member: discord.member.Member,
    time: float,
    _json_file_name: str = JSON_FILE_PATH_USERS_VOICE_CHANNEL_DATA,
) -> None:
    new_user_data: dict[str, float] = {"member_id": str(member.id), "time_joined": time}
    user_data = read_json_data(json_file=_json_file_name)
    user_data.append(new_user_data)
    write_json_data(json_file=_json_file_name, user_data=user_data)


async def remove_user_entry_from_voice_channel_data_and_add_xp(
    member: discord.member.Member,
    time: float,
    _json_file_name_vc: str = JSON_FILE_PATH_USERS_VOICE_CHANNEL_DATA,
    _json_file_name_db: str = JSON_FILE_PATH_USERS_LEVEL_DATA,
) -> None:
    # get user data
    user_data = read_json_data(json_file=_json_file_name_vc)

    # get time amount and remove entry to keep clean
    index_of_member_in_list = 0

    for i, user in enumerate(user_data):
        if user["member_id"] == str(member.id):
            joined_timestamp = user["time_joined"]
            index_of_member_in_list = i

    user_data.pop(index_of_member_in_list)

    # calculate time and xp points
    spent_time: int = int(time - joined_timestamp)
    experience_points: int = spent_time // 120

    logging.info(
        "User %s spent %s s in various voice chats and got %s xp",
        member.name,
        spent_time,
        experience_points,
    )

    # write new json data
    write_json_data(json_file=_json_file_name_vc, user_data=user_data)

    # add xp
    await add_experience_points_to_user(
        json_file_name=_json_file_name_db,
        member=member,
        experience_point_amount=experience_points,
    )


def get_xp_to_next_level(current_level: int, current_xp: int) -> List[int]:
    if current_level < 10:
        return [450 - current_xp, 10]
    elif current_level < 25:
        return [3000 - current_xp, 25]
    elif current_level < 50:
        return [12250 - current_xp, 50]
    elif current_level < 70:
        return [24150 - current_xp, 70]
    elif current_level < 80:
        return [31600 - current_xp, 80]
    elif current_level < 90:
        return [40050 - current_xp, 90]
    elif current_level < 100:
        return [49500 - current_xp, 100]
    else:
        return [0, 0]


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message):
        # check if message is from bot itself
        if message.author == self.user:
            return

        # delete message if it is in channel level
        if message.channel.id == LEVEL_CHANNEL_ID:
            await message.delete()
        else:
            logging.info(
                "User %s (%s) wrote message in '%s'",
                message.author.name,
                message.author.id,
                message.channel.name,
            )

            await add_experience_points_to_user(
                json_file_name=JSON_FILE_PATH_USERS_LEVEL_DATA,
                member=message.author,
                experience_point_amount=1,
            )

    async def on_voice_state_update(self, member, before, after):
        now: float = time.time()
        if not before.channel and after.channel:
            logging.info(
                "User %s (%s) joined '%s' at %s",
                member.name,
                member.id,
                after.channel.name,
                now,
            )
            # write json data
            add_new_user_entry_into_voice_channel_data(member=member, time=now)
        elif before.channel and after.channel:  # switching vcs, only for logging
            logging.info(
                "User %s (%s) changed to channel '%s' at %s",
                member.name,
                member.id,
                after.channel.name,
                now,
            )
        elif before.channel and not after.channel:
            logging.info(
                "User %s (%s) left '%s' at %s",
                member.name,
                member.id,
                before.channel.name,
                now,
            )

            await remove_user_entry_from_voice_channel_data_and_add_xp(
                member=member, time=now
            )


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True

activity = discord.Activity(
    type=discord.ActivityType.watching,
    name="you... try /my_level in the level channel :)",
)

client = Client(
    command_prefix="!", intents=intents, activity=activity, status=discord.Status.dnd
)


@client.tree.command(
    name="my_level",
    description="Get your current level!",
    guild=discord.Object(id=GUILD_ID),
)
async def my_level(interaction: discord.Interaction):
    if interaction.channel_id == LEVEL_CHANNEL_ID:
        user_data = read_json_data(json_file=JSON_FILE_PATH_USERS_LEVEL_DATA)

        user_index = 0
        for i, user in enumerate(user_data):
            if user["author_id"] == str(interaction.user.id):
                user_index = i

        current_user_data = user_data[user_index]

        required_experience_points_and_next_level = get_xp_to_next_level(
            current_level=current_user_data["level"],
            current_xp=current_user_data["experience_points"],
        )

        await interaction.response.send_message(
            f"{interaction.user.name} you are currently level {current_user_data['level']} and have {current_user_data['experience_points']} xp. You need atleast {required_experience_points_and_next_level[0]} xp to reach the next level: level {required_experience_points_and_next_level[1]}."
        )


client.run(DISCORD_TOKEN)
