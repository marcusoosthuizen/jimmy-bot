# jimmy-bot
A minimal discord bot that can display info about and control a minecraft / hytale server. It is also the official discord bot of Pigletmine!

When you first run the bot, a config file will be generated in .config/jimmy. Simply add your bot's token and the paths to your minecraft / hytale server in the config file and run! The style of messages are designed to look similar to the DiscordSRV plugin and in fact this bot is able to be run together with DiscordSRV 


Requirements:
- GNU Screen
- interactions.py and mojang python packages
- Standard GNU/Linux Packages


Command List:
- /help - Returns a list of every command Jimmy can perform
- /status - Displays the active game server and the players online
- /mc <start/stop> - Starts/Stops the Minecraft server
- /hy <start/stop> - Starts/Stops the Hytale server
