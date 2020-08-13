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

import getjobs

moderatorbotchan = None
botschan = None
testserverchan = None

testserverchanid = 726616838053691474
moderatorbotschanid = 698583349433860106
botschanid = 701578731554078761
welcomeid = 699456430175944785

serverid = 696005227521900596
testserverid = 726616837617614861

client = commands.Bot(command_prefix="!")
server = None
testserver = None

token = os.getenv("GRIMMBOT_TOKEN")

""" Globals for talks / schedule """
speakers = None
talks = None


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
    await welcomechan.send(outmsg)

# Set up globals on connection
@client.event
async def on_ready():
    global server
    global botschan
    global moderatorbotchan
    # Set up our objects
    if botschan is None:
        server = client.get_guild(serverid)
        testserver = client.get_guild(testserverid)
        botschan = server.get_channel(botschanid)
        moderatorbotchan = server.get_channel(moderatorbotschanid)
        testserverchan = testserver.get_channel(testserverchanid)
    await client.change_presence(activity=discord.Game(name="backdoors and breaches"))
    print("<hacker voice>I'm in</hacker voice>")
    print(client.user)

# END EVENT HANDLERS

# BEGIN COMMAND HANDLERS

# Command filter functions
def is_botcommands_channel(ctx):
    if ctx.message.channel.id in [botschanid, moderatorbotschanid, testserverchanid]:
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
        await ctx.send("Invalid input - Usage: !setwelcome <welcome message>\nTo include the user mention, add a {} for it. Currently only allowed once in the message.")
    try:
        welcomemessage = newmsg
        with open("welcomemsg.txt", "w") as fh:
            fh.write(newmsg)
        await ctx.send("Done, set welcome text.")
    except:
        await ctx.send("Threw an exception when trying to set the message.")

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins","GRIMM")
async def getwelcome(ctx):
    outmsg = ""
    try:
        outmsg = welcomemessage.format("USER")
    except:
        outmsg = welcomemessage
    await ctx.send("Current message:\n" + outmsg)

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins","GRIMM")
async def setstatus(ctx, statustype, *statustext):
    if statustype not in ["playing", "listening"]:
        await ctx.send("Invalid status type. Syntax: !setstatus <playing|listening> <status text>")
        return
    status = ' '.join(statustext)
    if status == "" or status is None:
        await ctx.send("You must enter status text. Syntax: !setstatus <playing|listening> <status text>")
        return
    try:
        if statustype == "listening":
            await client.change_presence(activity=discord.Game(name=status, type=2))
        else:
            await client.change_presence(activity=discord.Game(name=status))
        await ctx.send("Done. Status is now: " + ("listening to " if statustype == "listening" else "playing ") + status)
    except:
        await ctx.send("Something went wrong.\n")

#bans a user with a reason
@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins")
async def ban (ctx, member:discord.User=None, reason=None):
    if member == None or member == ctx.message.author:
        await ctx.send("You cannot ban yourself")
        return
    if reason == None:
        reason = "For being disruptive"
    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await server.ban(member, reason=reason)
    await ctx.send(f"{member} is banned!")

@client.command(pass_context=True, hidden=True)
@commands.has_any_role("mods","admins")
async def mute (ctx, member:discord.User=None, reason=None):
    if member == None or member == ctx.message.author:
        await ctx.send("You cannot mute yourself.")
        return
    if reason == None:
        reason = "For being disruptive"
    muterole = [role for role in server.roles if role.name == "muted"][0]
    await member.add_roles(member, muterole)
    await ctx.send(f"{member} is muted!")



# publicly available commands. Have to be used from the public bot channel unless you have GRIMM role


@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def role(ctx, subcmd, newrole):
    """ Add or remove a role. Valid roles: "blue-team", "red-team", "purple-team", "threat-hunting", "threat-modeling", "binary-analysis", "training", "CyPhy". """
    validroles = ["blue-team", "red-team", "purple-team", "threat-hunting", "threat-modeling", "binary-analysis", "training", "CyPhy"]
    replacements = {"blueteam": "blue-team", "redteam": "red-team", "purpleteam": "purple-team", "threathunting": "threat-hunting", "threatmodeling": "threat-modeling", "binaryanalysis": "binary-analysis", "cyphy": "CyPhy"}
    if newrole in replacements:
        newrole = replacements[newrole]
    if newrole not in validroles:
        await ctx.send("USAGE: !role <add|remove> <role>.\nInvalid role. Valid roles are: {}.".format(', '.join(validroles)))
        return
    roleobj = [role for role in server.roles if role.name == newrole][0]
    if subcmd == "add":
        if roleobj in ctx.message.author.roles:
            await ctx.send(f"You already have the {newrole} role!")
            return
        await ctx.message.author.add_roles(roleobj)
        await ctx.send(f"Done! You now have the {newrole} role!")
    elif subcmd == "remove" or subcmd == "rem":
        if roleobj not in ctx.message.author.roles:
            await ctx.send(f"You don't have the {newrole} role!")
            return
        await ctx.message.author.remove_roles(roleobj)
        await ctx.send(f"Done! Removed the {newrole} role!")
    else:
        await ctx.send("USAGE: !role <add|remove> <role>.\nInvalid subcommand. Valid subcommands are: add, remove.")

@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def jobcategories(ctx):
    """ Get a list of all open jobs. """
    await ctx.send("The following categories exist:\n{}".format("\n".join(getjobs.get_categories())))

@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def jobsincategory(ctx, category):
    """ Get a list of jobs in a specific category. """
    joblist = getjobs.get_jobs_in_category(category)
    if len(joblist) == 0:
        await ctx.send("No jobs found in the specified category.")
        return
    for job in joblist:
        output = getjobs.formatjob(job)
        if len(output) > 2000:
            for i in range(1, len(output), 2000):
                await ctx.author.send(output[i:i+2000])
        else:
            await ctx.author.send(getjobs.formatjob(job))
    await ctx.send("The reply is probably long. Check your DMs")


@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def jobsall(ctx):
    """ Get a list of all open jobs. """
    joblist = getjobs.get_all_jobs()
    if len(joblist) == 0:
        await ctx.send("No jobs found. Since we're probably hiring, this is probably a bug")
        return
    for job in joblist:
        output = getjobs.formatjob(job)
        if len(output) > 2000:
            for i in range(1, len(output), 2000):
                await ctx.author.send(output[i:i+2000])
        else:
            await ctx.author.send(getjobs.formatjob(job))
    await ctx.send("The reply is probably long. Check your DMs")


'''
"""
    Talks will have a speaker and a time
    Speakers will have a name and a bio

    talks = list({trackone = list(), tracktwo = list()}) # one list for track 1, one for track 2
    speakers = list() # a list of speaker dicts() - keys will be name and bio
"""

# TODO: make various time formats work
# TODO: include the track alongside the talks
# TODO: print the track when printing a talk


def initializeSpeakers():
    """
        Initialize the list of speakers if not already initialized.
        Tries to load from speakers.pickle, on failure creates empty list
    """
    global speakers    
    if speakers is not None:
        return
    # try to load speakers from a file, if it fails, initialize it
    try:
        with open("speakers.pickle", "rb") as fh:
            speakers = pickle.load(fh)
    except FileNotFoundError:
        speakers = list()
        saveSpeakers()

def initializeTalks():
    global talks
    if talks is not None:
        return
    try:
        with open("talks.pickle", "rb") as fh:
            talks = pickle.load(fh)
    except FileNotFoundError:
        talks = dict()
        talks["trackone"] = list()
        talks["tracktwo"] = list()
        saveTalks()

def saveTalks():
    with open("talks.pickle", "wb") as fh:
        pickle.dump(talks, fh)

def saveSpeakers():
    with open("speakers.pickle", "wb") as fh:
        pickle.dump(speakers, fh)

@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def listspeakers(ctx):
    """
        Get a list of all speakers
    """
    outstr = ""
    for index in range(len(speakers)):
        outstr += "{:02d}: {}\n".format(index + 1, speakers[index]["name"])
    if len(outstr):
        await ctx.send(outstr)
    else:
        await ctx.send("No speakers are in the list; this might be a bug.")

@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def speaker(ctx, whichspeaker):
    """
        Query the bio for a speaker by name or speaker id
    """
    bynum = False
    # determine if we were given a number or a name
    if whichspeaker.isdigit():
        bynum = True
        which = int(whichspeaker) - 1
    else:
        which = whichspeaker
    if bynum:
        # determine if it's a valid index
        if which > len(speakers):
            await ctx.send("Invalid speaker index. Max value is {}".format(len(speakers) + 1))
            return
        if which < 0:
            await ctx.send("Invalid speaker index. The list starts at 1.")
            return
        # return the info
        bio = speakers[which]["bio"]
        name = speakers[which]["name"]
    else:
        # Determine if the name is in the list
        matches = [speaker for speaker in speakers if speaker["name"].lower() == which.lower()]
        if len(matches) == 0:
            await ctx.send("Invalid speaker. Get the full list using !listspeakers")
            return
        bio = matches[0]["bio"]
        name = matches[0]["name"]
    await ctx.send(f"{name}:\n{bio}")

# TODO: abstract the duplicate code from these two funcs to a new function
@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def listtalks(ctx, track=None):
    """
        Query the list of all talks (optionally in a specific track)
    """
    if track is None:
        alltalks = talks["trackone"] + talks["tracktwo"]
    elif track in ["1", "one"]:
        alltalks = talks["trackone"]
    elif track in ["2", "two"]:
        alltalks = talks["tracktwo"]
    else:
        await ctx.send("Invalid track. Options are: one, two")
        return

    times = [talk["time"] for talk in alltalks]
    times.sort()
    outstr = ""
    if len(alltalks) == 0:
        await ctx.send("There are no talks in the schedule. This might be a bug.")
        return

    for time in times:
        # TODO: this is not optimized because I didn't store the indices, so if the number goes up, refactor this
        talks_at_time = [talk for talk in alltalks if talk["time"] == time]
        for talk in talks_at_time:
            print(talk)
        titles = [talk["title"] for talk in talks_at_time]
        # By dynamically creating the format string here and expanding twice via format calls
        # this works for any number of talks at the given time.
        outstr += "{}: {}\n".format(talks_at_time[0]["time"], " | ".join(["{}"]*len(talks_at_time)).format(*titles))
    await ctx.send(outstr)


@client.command(pass_context=True)
@commands.check(is_botcommands_channel)
async def talk(ctx, name_or_time, track=None):
    """
        Query a specific talk by name or by time; if specifying time, can also specify track
    """
    bynum = False
    # TODO: add real time parsing so that you don't have to enter 0900
    # something like: remove colon, check if it's numeric, then pad to 4 characters
    if track is None:
        alltalks = talks["trackone"] + talks["tracktwo"]
    elif track in ["1", "one"]:
        alltalks = talks["trackone"]
    elif track in ["2", "two"]:
        alltalks = talks["tracktwo"]
    else:
        await ctx.send("Invalid track. Options are: one, two")
        return
    bynum = False
    # determine if we were given a number or a name
    if name_or_time.isdigit():
        bynum = True
        which = int(name_or_time)
    else:
        which = name_or_time
    if bynum:
        # get all talks at that time
        talks_at_time = [talk for talk in alltalks if talk["time"] == which]
    else:
        # get all talks by title
        talks_at_time = [talk for talk in alltalks if talk["title"].lower() == which]
    
    if len(talks_at_time) == 0:
        await ctx.send("No talks matched your query.")
        return

    # By dynamically creating the format string here and expanding twice via format calls
    # this works for any number of talks at the given time.
    titles = [talk["title"] for talk in talks_at_time]
    outstr = "{}: {}".format(talks_at_time[0]["time"], " | ".join(["{}"]*len(talks_at_time)).format(*titles))
    await ctx.send(outstr)

def addspeaker_helper(name, bio):
    speakers.append({"name": name, "bio": bio})
    saveSpeakers()

@client.command(pass_context=True)
@commands.has_any_role("mods","admins","GRIMM")
async def addtalk(ctx, talktitle, speakername, time, track, speakerbio=None):
    """
        Add a new talk to the schedule at the specified time. If the speakername doesn't already exist, create it
    """
    # input validation on track
    if track in ["1", "one", "trackone"]:
        track = "trackone"
    elif track in ["2", "two", "tracktwo"]:
        track = "tracktwo"
    else:
        await ctx.send("You must specify a track. Valid tracks: one, two")
        return

    # see if the talk title exists, give them an error saying to use modify
    alltalks = talks["trackone"] + talks["tracktwo"]
    if len(alltalks):
        matching = [talk for talk in talks if talks["title"].lower == talktitle.lower()]
        if len(matching):
            await ctx.send("A talk with that title exists. Modify it with !modifytalk \"{}\" \"{}\" (and optionally also set the time".format(talktitle, speakername))
            return
    # determine if the speakername exists
    matches = [speaker for speaker in speakers if speaker["name"].lower() == speakername.lower()]
    if len(matches) == 0:
        if speakerbio is None:
            await ctx.send("No speaker by that name exists. To create a new one, also supply a bio:\n!addtalk \"{}\" \"{}\" \"{}\" \"{}\" \"speaker bio\"".format(talktitle, speakername, time, track))
            return
        addspeaker_helper(speakername, speakerbio)
    # create talk entry with speaker
    talk = {"title": talktitle, "time": time, "speaker": speakername}
    talks[track].append(talk)
    await ctx.send("Added.")
    saveTalks()

@client.command(pass_context=True)
@commands.has_any_role("mods","admins","GRIMM")
async def addspeaker(ctx, name, bio):
    # determine if the speaker already exists. If so, tell them to use modify
    matches = [speaker for speaker in speakers if speaker["name"].lower() == which.lower()]
    if len(matches):
        await ctx.send("That speaker already exists. To modify:\n!modifyspeaker \"{}\" \"speaker bio\"".format(name))
        return
    addspeaker(name, bio)
    await ctx.send("Added.")

@client.command(pass_context=True)
@commands.has_any_role("mods","admins","GRIMM")
async def modifytalk(ctx, talk, newtitle, speaker=None, time=None, newtrack=None):
    """
        Modify an existing talk to change its title, speaker, and time
    """
    # determine if the talk exists
    alltalks = talks["trackone"] + talks["tracktwo"]
    print(newtitle.lower())
    matching = [matchtalk for matchtalk in alltalks if matchtalk["title"].lower() == newtitle.lower()]
    print(matching)
    if len(matching) == 0:
        await ctx.send("No talk with that title exists. Create it with !addtalk \"{}\" \"{}\" (and optionally also set the time".format(newtitle, speaker))
        return

    talk = matching[0]
    # set the new title
    talk["title"] = newtitle
    # if given new speaker, set that
    if speaker is not None:
        talk["speaker"] = speaker
    # if given new time, set that
    if time is not None:
        talk["time"] = time
    # if given newtrack set that
    if newtrack is not None:
        # validate it's a valid track
        if newtrack in ["1", "one", "trackone"]:
            newtrack = "trackone"
        elif newtrack in ["2", "two", "tracktwo"]:
            newtrack = "tracktwo"
        else:
            await ctx.send("Invalid track. Options are: one, two. Other modifications were still made")
            return
        talk["track"] = newtrack
    await ctx.send("Done.")
    saveTalks()

#TODO: a setbio command for bios with spaces in them, because this breaks modifyspeaker

@client.command(pass_context=True)
@commands.has_any_role("mods","admins","GRIMM")
async def modifyspeaker(ctx, speaker, newname=None, newbio=None):
    # something must be modified.
    if newname is None:
        await ctx.send("You must specify something to modify.\n!modifyspeaker \"{}\" \"new name\" \"new bio\"".format(speaker))
        return
    # check if it's numeric
    bynum = False
    # determine if we were given a number or a name
    if speaker.isdigit():
        bynum = True
        which = int(speaker) - 1
    else:
        which = speaker
    if bynum:
        # determine if it's a valid index
        if which > len(speakers):
            await ctx.send("Invalid speaker index. Max value is {}".format(len(speakers) + 1))
            return
        if which < 0:
            await ctx.send("Invalid speaker index. The list starts at 1.")
            return
        speakers[which]["name"] = newname
        if newbio is not None:
            speakers[which]["bio"] = newbio
    else:
        # not by num
        matches = [speaker for speaker in speakers if speaker["name"].lower() == which.lower()]
        if len(matches) == 0:
            await ctx.send("Invalid speaker. Get the full list using !listspeakers")
            return
        matches[0]["name"] = newname
        if newbio is not None:
            matches[0]["bio"] = newbio
    await ctx.send("Done.")
    saveSpeakers()
'''

# END COMMAND HANDLERS


#initializeSpeakers()
#initializeTalks()
server = client.get_guild(serverid)
client.run(token)

try:
    with open("welcomemsg.txt", "r") as fh:
        welcomemessage = fh.read()
except:
    welcomechan = server.get_channel(welcomeid)
    welcomemessage = "Welcome to the GRIMM public discord, {}! Please take a look at " + welcomechan.mention + " and the pinned post there to understand the Code of Conduct!"


