## Imports ##
import io
from os import makedirs
from os import popen as cmd
from time import sleep

import tomllib
from interactions import (
    Client,
    Embed,
    Intents,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    listen,
    slash_command,
    slash_option,
)
from mojang import API

## Bot Init ##
bot = Client(intents=Intents.DEFAULT)
api = API()


##################
# Config Loading #
##################


data = None
valid = False
home = cmd("cd ~;pwd").read()[:-1]

try:
    ## Attempts to open config file located in .config ##
    with open(f"{home}/.config/jimmy/config.toml", "rb") as f:
        data = tomllib.load(f)
except:
    makedirs(f"{home}/.config/jimmy", exist_ok=True)

    ## Creates a template config in .config
    with open(f"{home}/.config/jimmy/config.toml", "w") as f:
        f.write(
            '###########\n# General #\n###########\n\n# The discord bot\'s private token\nbot-token = ""\n\n\n#############\n# Minecraft #\n#############\n\n# enables minecraft functionality\nmc-enabled = false\n\n# The path to the server directory\nmc-path = ""\n\n# Command to execute to start the server (can be absolute path or path relative to mc-path)\nmc-exec = ""\n\n\n##########\n# Hytale #\n##########\n\n# enables hytale functionality\nhy-enabled = false\n\n# The path to the server directory\nhy-path = ""\n\n# Command to execute to start the server (can be absolute path or path relative to hy-path)\nhy-exec = ""'
        )
    print(
        f"Config file has been generated in {home}/.config/jimmy/config.toml\nPlease add your bot's token and other settings relating to your minecraft and/or hytale server"
    )

## Checks if data in config is valid ##
if data != None:
    if data["bot-token"] == "":
        print("No bot token in config file")
    elif data["mc-enabled"] and data["mc-path"] == "":
        print("No mc-path defined in config file")
    elif data["mc-enabled"] and data["mc-exec"] == "":
        print("No mc-exec defined in config file")
    elif data["hy-enabled"] and data["hy-path"] == "":
        print("No hy-path defined in config file")
    elif data["hy-enabled"] and data["hy-exec"] == "":
        print("No hy-exec defined in config file")
    else:
        valid = True


####################
# Shared Functions #
####################


## returns whether a game (minecraft or hytale) is online ##
def check(game):
    if game in cmd("screen -ls").read():
        return True
    return False


## returns a list containing the players online in minecraft ##
def mc_players():
    ## runs the list command inside of minecraft ##
    cmd('screen -S minecraft -X stuff "list\n"')
    sleep(0.25)

    ## retrieves the line in logs containing the output of /list ##
    logs = cmd(f"tail -10 {data['mc-path']}/logs/latest.log").read().split("\n")
    for i in reversed(logs):
        if (
            "[Server thread/INFO] [net.minecraft.server.MinecraftServer/]: There are"
            in i
        ):
            logs = i
            break

    ## extracts the usernames and returns them ##
    playernum = logs.split("There are ")[1].split(" of a max")[0]
    if int(playernum) == 0:
        return []
    return logs.split("players online:")[1].split(",")


def hy_players():
    ## runs the who command inside of hytale ##
    cmd('screen -S hytale -X stuff "/who\n"')
    sleep(0.25)

    ## retrieves the line in logs containing the output of /who ##
    logs = cmd(f"ls {data['hy-path']}/logs").read().split(" ")[0]
    print(logs)
    logs = cmd(f"tail -10 {data['hy-path']}/logs/{logs}").read().split("\n")

    for i in reversed(logs):
        if "PigletTale (" in i:
            logs = i
            break

    ## extracts the usernames, formats and returns them ##
    playernum = logs.split("PigletTale (")[1].split("): :")[0]
    if int(playernum) == 0:
        return []
    raw_pl = logs.split("): : ")[1].split(", ")
    for i in range(len(raw_pl)):
        raw_pl[i] = raw_pl[i].split(" (")[0]
    return raw_pl


################
# Bot Commands #
################


@listen()
async def on_ready():
    print("\n       --- Bot Online ---       ")
    print(f"This bot is owned by {bot.owner}\n")


## Help command ##
@slash_command(
    name="help", description="Returns a list of every command Jimmy can perform"
)
async def help(ctx: SlashContext):
    await ctx.send(
        content="📜 **Command List:**",
        embeds=[
            Embed(
                color=42,
                fields=[
                    {
                        "name": "/help",
                        "value": "Returns a list of every command Jimmy can perform",
                    },
                    {
                        "name": "/status",
                        "value": "Displays the active game server and the players online",
                    },
                    {
                        "name": "/mc - <start/stop>",
                        "value": "Starts/Stops the Minecraft server",
                    },
                    {
                        "name": "/hy - <start/stop>",
                        "value": "Starts/Stops the Hytale server",
                    },
                ],
            )
        ],
    )


## Status command ##
@slash_command(
    name="status",
    description="Displays the active game server and the players online",
)
async def status(ctx: SlashContext):
    ## Minecraft Specific Status ##
    if check("minecraft"):
        pl_list = mc_players()
        if pl_list == []:
            await ctx.send(
                content=f":fire: **Active Server: Minecraft**\n👾 **Players Online (0):**",
                embeds=[
                    Embed(
                        color=42,
                        author={
                            "name": "There are no players online",
                            "icon_url": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%2Fid%2FOIP.AA4OkV7kG0EV4kwKh2K2RAAAAA%3Fpid%3DApi&f=1&ipt=8c79f438144c0d83c77d6d41b674725e5823e8a401e8f548d50b1310fffe731b",
                        },
                    ),
                ],
            )
        else:
            pl_embeds = []
            for pl in pl_list:
                pl_embeds.append(
                    Embed(
                        color=42,
                        author={
                            "name": pl,
                            "icon_url": f"https://cravatar.eu/helmavatar/{pl.split(' ')[1]}/256.png",
                        },
                    )
                )

            await ctx.send(
                content=f":fire: **Active Server: Minecraft**\n👾 **Players Online ({len(pl_list)}):**",
                embeds=pl_embeds,
            )
    ## Hytale Specific Status ##
    if check("hytale"):
        pl_list = hy_players()
        if pl_list == []:
            await ctx.send(
                content=f":fire: **Active Server: Hytale**\n👾 **Players Online (0):**",
                embeds=[
                    Embed(
                        color=42,
                        author={
                            "name": "There are no players online",
                            "icon_url": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%2Fid%2FOIP.AA4OkV7kG0EV4kwKh2K2RAAAAA%3Fpid%3DApi&f=1&ipt=8c79f438144c0d83c77d6d41b674725e5823e8a401e8f548d50b1310fffe731b",
                        },
                    ),
                ],
            )
        else:
            pl_embeds = []
            for pl in pl_list:
                pl_embeds.append(
                    Embed(
                        color=42,
                        author={
                            "name": pl,
                            "icon_url": f"https://hyvatar.io/render/{pl}",
                        },
                    )
                )

            await ctx.send(
                content=f":fire: **Active Server: Hytale**\n👾 **Players Online ({len(pl_list)}):**",
                embeds=pl_embeds,
            )
    ## If neither server is active ##
    else:
        await ctx.send(":sleeping: **The server is currently offline**")


## mc-start command ##
@slash_command(name="mc-start", description="Starts the Minecraft server")
async def mc_start(ctx: SlashContext):
    if check("minecraft"):
        await ctx.send(":face_with_monocle: **The minecraft server is already online**")
    elif check("hytale"):
        await ctx.send(
            ":cold_sweat: **The hytale server is online right now. Please stop it before starting the server**"
        )
    else:
        cmd(f"cd {data['mc-path']};screen -dmS minecraft {data['mc-exec']}")
        await ctx.send(":alarm_clock: **Server starting...**")


## mc-stop command ##
@slash_command(name="mc-stop", description="Stops the Minecraft server")
async def mc_stop(ctx: SlashContext):
    if check("minecraft"):
        if len(mc_players()) == 0:
            cmd('screen -S minecraft -X stuff "stop\n"')
            await ctx.send(":alarm_clock: **Server stopping...**")
        else:
            await ctx.send(
                ":face_with_raised_eyebrow: **There are players online, don't ruin their fun...**"
            )
    else:
        await ctx.send(":face_with_monocle: **The server is already offline**")


## hy-start command ##
@slash_command(name="hy-start", description="Starts the Hytale server")
async def hy_start(ctx: SlashContext):
    if check("hytale"):
        await ctx.send(":face_with_monocle: **The hytale server is already online**")
    elif check("minecraft"):
        await ctx.send(
            ":cold_sweat: **The minecraft server is online right now. Please stop it before starting the server**"
        )
    else:
        cmd(f"cd {data['hy-path']}/logs;rm *.log")
        cmd(f"cd {data['hy-path']};screen -dmS hytale {data['hy-exec']}")
        await ctx.send(":alarm_clock: **Server starting...**")


## hy-stop command ##
@slash_command(name="hy-stop", description="Stops the Hytale server")
async def hy_stop(ctx: SlashContext):
    if check("hytale"):
        if len(hy_players()) == 0:
            cmd('screen -S hytale -X stuff "/stop\n"')
            await ctx.send(":alarm_clock: **Server stopping...**")
        else:
            await ctx.send(
                ":face_with_raised_eyebrow: **There are players online, don't ruin their fun...**"
            )
    else:
        await ctx.send(":face_with_monocle: **The server is already offline**")


## starts the bot ##
if valid:
    bot.start(data["bot-token"])
