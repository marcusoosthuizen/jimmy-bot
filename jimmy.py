from interactions import Client, Intents, listen
from interactions import slash_command, SlashContext, Embed
from os import popen as cmd
from time import sleep
from mojang import API

bot = Client(intents=Intents.DEFAULT)
api = API()

## Loads Config File ##
data = None
valid = False
try:
    with open("jimmy.toml", "rb") as f:
        data = tomllib.load(f)
    if data['jar-path'][-1] != "/":
      data['jar-path'] += "/"
    print(data['jar-path'])
except:
    with open("jimmy.toml", "w") as f:
        f.write('# The discord bot\'s private token\nbot-token = ""\n\n# The path to the directory that contains the minecraft server jar  e.g. /home/mc-server/\njar-path = ""\n\n# The name of the minecraft server jar\njar-name = "server.jar"\n\n# The amount of ram in gb to allocate to the server\nram = 6')
    print("Config file generated!\nPlease add your bot's token, the path to your server jar and the name of your server jar in jimmy.toml")

if data != None:
    if data['bot-token'] == "":
        print("Invalid bot token in jimmy.toml")
    elif data['jar-path'] == "":
        print("Invalid jar path in jimmy.toml")
    elif data['jar-name'] == "":
        print("Invalid jar name in jimmy.toml")
    elif type(data['ram']) != int:
        print("Invalid ram amount in jimmy.toml") 
    else:
        valid = True


@listen()
async def on_ready():
    print("\n       --- Bot Online ---       ")
    print(f"This bot is owned by {bot.owner}\n")


@slash_command(name="server-help", description="Returns a list of every command Jimmy can perform")
async def server_help(ctx: SlashContext):
  await ctx.send(content="📜 **Command List (5):**", embeds=[Embed(
      color=255,
      fields=[
        {
          "name" : "/server-help",
          "value" : "Returns a list of every command Jimmy can perform"
        },
        {
          "name" : "/server-start",
          "value" : "Starts the mc server"
        },
        {
          "name" : "/server-stop",
          "value" : "Stops the mc server"
        },
        {
          "name" : "/server-status",
          "value" : "Displays info about the mc server's current state"
        },
        {
          "name" : "/server-players",
          "value" : "Shows a list of the players currently online"
        }
      ])])


@slash_command(name="server-start", description="Starts the mc server")
async def server_start(ctx: SlashContext):
  if "minecraft" in cmd('screen -ls').read():
    await ctx.send(":face_with_monocle: **The server is already online**")
  else:
    cmd(f"cd {data['jar-path']};screen -dmS minecraft java -Xms6G -Xmx6G -jar {data['jar-name']} --nogui")
    await ctx.send(":alarm_clock: **Server starting...**")


@slash_command(name="server-stop", description="Stops the mc server")
async def server_stop(ctx: SlashContext):
  if "minecraft" in cmd('screen -ls').read():
    cmd('screen -S minecraft -X stuff "list\n"')
    sleep(0.25)
    logs = cmd(f"tail -10 {data['jar-path']}logs/latest.log").read().split("\n")
    for i in reversed(logs):
      if "[Server thread/INFO]: There are" in i:
        logs = i;break
    playernum = logs.split("There are ")[1].split(" of a max")[0]

    if int(playernum) == 0:
      cmd('screen -S minecraft -X stuff "stop\n"')
      await ctx.send(":alarm_clock: **Server stopping...**")
    else:
      await ctx.send(":face_with_raised_eyebrow: **There are players online, don't ruin their fun...**")
  else:
    await ctx.send(":face_with_monocle: **The server is already offline**")


@slash_command(name="server-status", description="Displays info about the mc server's current state")
async def server_status(ctx: SlashContext):
  if "minecraft" in cmd('screen -ls').read():
    await ctx.send(":laughing: **The server is currently online!**")
  else:
    await ctx.send(":sleeping: **The server is currently offline**")


@slash_command(name="server-players", description="Shows a list of the players currently online")
async def server_players(ctx: SlashContext):
  if "minecraft" in cmd('screen -ls').read():
    cmd('screen -S minecraft -X stuff "list\n"')
    sleep(0.25)
    logs = cmd(f"tail -10 {data['jar-path']}/logs/latest.log").read().split("\n")
    for i in reversed(logs):
      if "[Server thread/INFO]: There are" in i:
        logs = i;break
    
    playernum = logs.split("There are ")[1].split(" of a max")[0]
    if int(playernum) == 0:
      await ctx.send(content=f":scroll: **Players Online ({playernum}):**",embeds=[Embed(color=255,author={"name": "There are no players online","icon_url": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn1.iconfinder.com%2Fdata%2Ficons%2Flogos-brands-in-colors%2F231%2Famong-us-player-red-512.png&f=1&nofb=1&ipt=275e7fa2525a2ce400f185b87039198033b5c5ecca156b2f83acd8c50d68863d&ipo=images"}),])
    else:
      players = logs.split("players online:")[1].split(",")
      playerembeds = []
      for player in players:
        playerembeds.append(Embed(color=255,author={
          "name" : player,
          "icon_url" : f'https://cravatar.eu/helmavatar/{player.split(" ")[1]}/256.png'
        }))

      await ctx.send(content=f":scroll: **Players Online ({playernum}):**",embeds=playerembeds)
  else:
    await ctx.send(content=f":scroll: **Players Online (0):**",embeds=[Embed(color=255,author={"name": "There are no players online","icon_url": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn1.iconfinder.com%2Fdata%2Ficons%2Flogos-brands-in-colors%2F231%2Famong-us-player-red-512.png&f=1&nofb=1&ipt=275e7fa2525a2ce400f185b87039198033b5c5ecca156b2f83acd8c50d68863d&ipo=images"}),])



if valid: bot.start(data['bot-token'])