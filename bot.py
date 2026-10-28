## Imports ##
from os import popen as cmd
from time import sleep

from interactions import (
    Client,
    Embed,
    EmbedAuthor,
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


#################
# Configuration #
#################

token = "TOKEN" # discord token
servers = ["smp", "pvp"] # names of server dirs (no slashes)
dir = ".." # relative or exact path to folder containing servers

####################
# Shared Functions #
####################


## returns whether a server is online ##
def check(server):
    return server in cmd("screen -ls").read()


## returns a list containing the players online in minecraft ##
def players():
    server = None
    for i in servers:
        if check(i):
            server = i

    if not server:
        return None

    ## runs the list command inside of minecraft ##
    cmd(f'screen -S {server} -X stuff "list\n"')
    sleep(0.25)

    ## retrieves the line in logs containing the output of /list ##
    logs = cmd(f"tail -10 {dir}/{server}/logs/latest.log").read().split("\n")
    for i in reversed(logs):
        if ("[Server thread/INFO]: System chat: There are" in i or "INFO]: There are" in i):
            logs = i
            break

    ## extracts the usernames and returns them ##
    if type(logs) is str:
        playernum = logs.split("There are ")[1].split(" of a max")[0]
        if int(playernum) == 0:
            return []
        return logs.split("players online:")[1].split(",")
    return None

def stop():
    server = None
    for i in servers:
        if check(i):
            server = i

    if server:
        cmd(f'screen -S {server} -X stuff "stop\n"')
        sleep(1)
        timeout = 0
        while not "No Sockets" in cmd("screen -ls").read() and timeout < 10:
            sleep(1)
            timeout += 1

def start(server):
    cmd(f"cd {dir}/{server};screen -dmS {server} ./run.sh")

################
# Bot Commands #
################


@listen()
async def on_ready():
    print("\n       --- Bot Online ---       ")
    print(f"This bot is owned by {bot.owner}\n")
    print(f"Bot is in {len(bot.guilds)} servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")


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
                        "value": "Displays the active mc server and the players online",
                    },
                    {
                        "name": "/switch <server>",
                        "value": "Swaps the active mc server with the one selected",
                    },
                ],
            )
        ],
    )


## Status command ##
@slash_command(
    name="status",
    description="Displays the active mc server and the players online",
)
async def status(ctx: SlashContext):
    server = None
    for i in servers:
        if check(i):
            server = i

    if server:
        pl_list = players()
        if pl_list != None:
            if pl_list == []:
                await ctx.send(
                    content=f":fire: **Active: {server.upper()} Server**\n👾 **Players Online (0):**",
                    embeds=[
                        Embed(
                            color=42,
                            author=EmbedAuthor(
                                name="There are no players online",
                                icon_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%2Fid%2FOIP.AA4OkV7kG0EV4kwKh2K2RAAAAA%3Fpid%3DApi&f=1&ipt=8c79f438144c0d83c77d6d41b674725e5823e8a401e8f548d50b1310fffe731b",
                            ),
                        ),
                    ],
                )
            else:
                pl_embeds = []
                for pl in pl_list:
                    pl_embeds.append(
                        Embed(
                            color=42,
                            author=EmbedAuthor(
                                name=pl,
                                icon_url=f"https://cravatar.eu/avatar/{pl.split(' ')[1]}/256.png",
                            ),
                        )
                    )

                await ctx.send(
                    content=f":fire: **Active: {server.upper()} Server**\n👾 **Players Online ({len(pl_list)}):**",
                    embeds=pl_embeds,
                )
        else:
            await ctx.send(f":skull: **An error occured getting player count on the {server.upper()} Server**")
    else:
        await ctx.send(":sleeping: **All mc servers are currently offline**")

server_choices = []
for server in servers:
    server_choices.append(SlashCommandChoice(name=server.upper() + " Server", value=server))

## switch command ##
@slash_command(name="switch", description="Swaps the active mc server with the one selected")
@slash_option(
    name="server_choice",
    description="Server Option",
    required=True,
    opt_type=OptionType.STRING,
    choices=server_choices
)
async def switch(ctx: SlashContext, server_choice: str):

    if check(server_choice):
        await ctx.send(f":face_with_monocle: **The {server_choice} server is already online**")
    else:
        pl = players()
        if pl and len(pl) != 0:
            await ctx.send(
                ":face_with_raised_eyebrow: **There are players online, don't ruin their fun...**"
            )
        else:
            await ctx.send(":alarm_clock: **Swapping servers...**")
            stop()
            start(server_choice)


bot.start(token)
