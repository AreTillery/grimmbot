from discord.ext import commands
import discord
import os
import urllib.request
import json
import re
import pickle
import asyncio
import time
from datetime import datetime, timedelta

moderatorbotchan = None
botschan = None

moderatorbotschanid = "698583349433860106"
botschanid = "701578731554078761"
welcomeid = "699456430175944785"

serverid = "696005227521900596"

client = commands.Bot(command_prefix="~")
server = None

token = os.getenv("GRIMMBOT_TOKEN")

# BEGIN EVENT HANDLERS

# When a user connects, send a welcome message.
@client.event
async def on_member_join(member):
    welcomechan = server.get_channel(welcomeid)
    outmsg = ""
    try:
        outmsg = welcomemessage.format(member.mention)
    except:
        outmsg = welcomemessage
    await client.send_message(welcomechan, outmsg)

# Set up globals on connection
@client.event
async def on_ready():
    global server
    global botschan
    global moderatorbotchan
    # Set up our objects
    if botschan is None:
        server = client.get_server(serverid)
        botschan = server.get_channel(botschanid)
        moderatorbotchan = server.get_channel(moderatorbotschanid)
#    await client.change_presence(game=discord.Game(name="sounds of Hacking", type=2))
    await client.change_presence(game=discord.Game(name="backdoors and breaches"))
    print("<hacker voice>I'm in</hacker voice>")
    print(client.user)

# END EVENT HANDLERS

# BEGIN COMMAND HANDLERS

# Command filter functions
def is_botcommands_channel(ctx):
    if ctx.message.channel.id in [botschanid, moderatorbotschanid]:
        return True
    role = discord.utils.find(lambda r: r.name.lower() == "grimm", ctx.message.server.roles)
    if role in ctx.message.author.roles:
        return True
    return False

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins","GRIMM")
async def setwelcome(ctx, *args):
    global welcomemessage
    newmsg = ' '.join(args)
    if newmsg == "" or newmsg is None:
        await client.send_message(ctx.message.channel, "Invalid input - Usage: ~setwelcome <welcome message>\nTo include the user mention, add a {} for it. Currently only allowed once in the message.")
    try:
        welcomemessage = newmsg
        with open("welcomemsg.txt", "w") as fh:
            fh.write(newmsg)
        await client.send_message(ctx.message.channel, "Done, set welcome text.")
    except:
        await client.send_message(ctx.message.channel, "Threw an exception when trying to set the message.")

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins","GRIMM")
async def getwelcome(ctx):
    outmsg = ""
    try:
        outmsg = welcomemessage.format("USER")
    except:
        outmsg = welcomemessage
    await client.send_message(ctx.message.channel, "Current message:\n" + outmsg)

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins","GRIMM")
async def setstatus(ctx, statustype, *statustext):
    if statustype not in ["playing", "listening"]:
        await client.send_message(ctx.message.channel, "Invalid status type. Syntax: ~setstatus <playing|listening> <status text>")
        return
    status = ' '.join(statustext)
    if status == "" or status is None:
        await client.send_message(ctx.message.channel, "You must enter status text. Syntax: ~setstatus <playing|listening> <status text>")
        return
    try:
        if statustype == "listening":
            await client.change_presence(game=discord.Game(name=status, type=2))
        else:
            await client.change_presence(game=discord.Game(name=status))
        await client.send_message(ctx.message.channel, "Done. Status is now: " + ("listening to " if statustype == "listening" else "playing ") + status)
    except:
        await client.send_message(ctx.message.channel, "Something went wrong.\n")

#bans a user with a reason
@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins")
async def ban (ctx, member:discord.User=None, reason=None):
    if member == None or member == ctx.message.author:
        await client.send_message(ctx.message.channel, "You cannot ban yourself")
        return
    if reason == None:
        reason = "For being disruptive"
    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await server.ban(member, reason=reason)
    await client.send_message(ctx.message.channel, f"{member} is banned!")

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins")
async def mute (ctx, member:discord.User=None, reason=None):
    if member == None or member == ctx.message.author:
        await client.send_message(ctx.message.channel, "You cannot mute yourself.")
        return
    if reason == None:
        reason = "For being disruptive"
    muterole = [role for role in server.roles if role.name == "muted"][0]
    await client.add_roles(member, muterole)
    await client.send_message(ctx.message.channel, f"{member} is muted!")



# publicly available commands. Have to be used from the public bot channel unless you have GRIMM role

@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def role(ctx, subcmd, newrole):
    """ Add or remove a role. Valid roles: "blue-team", "red-team", "purple-team", "threat-hunting", "threat-modeling", "binary-analysis", "training" """
    validroles = ["blue-team", "red-team", "purple-team", "threat-hunting", "threat-modeling", "binary-analysis", "training"]
    if newrole not in validroles:
        await client.send_message(ctx.message.channel, "USAGE: ~role <add|remove> <role>.\nInvalid role. Valid roles are: {}.".format(', '.join(validroles)))
        return
    roleobj = [role for role in server.roles if role.name == newrole][0]
    if subcmd == "add":
        if roleobj in ctx.message.author.roles:
            await client.send_message(ctx.message.channel, f"You already have the {newrole} role!")
            return
        await client.add_roles(ctx.message.author, roleobj)
        await client.send_message(ctx.message.channel, f"Done! You now have the {newrole} role!")
    elif subcmd == "remove" or subcmd == "rem":
        if roleobj not in ctx.message.author.roles:
            await client.send_message(ctx.message.channel, f"You don't have the {newrole} role!")
            return
        await client.remove_roles(ctx.message.author, roleobj)
        await client.send_message(ctx.message.channel, f"Done! Removed the {newrole} role!")
    else:
        await client.send_message(ctx.message.channel, "USAGE: ~role <add|remove> <role>.\nInvalid subcommand. Valid subcommands are: add, remove.")

# END COMMAND HANDLERS

server = client.get_server(serverid)
client.run(token)

try:
    with open("welcomemsg.txt", "r") as fh:
        welcomemessage = fh.read()
except:
    welcomechan = server.get_channel(welcomeid)
    welcomemessage = "Welcome to the GRIMM public discord, {}! Please take a look at " + welcomechan.mention + " and the pinned post there to understand the Code of Conduct!"


