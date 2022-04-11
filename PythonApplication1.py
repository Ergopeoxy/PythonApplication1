
import discord
import os
import requests
import json
import random
import wikipedia
import youtube_dl
import wolframalpha
#import nacl
from replit import db
from keep_alive import keep_alive
# import pynacl
# import nacl
import os, platform
try:
    import nacl
except ImportError:
    try:
        if platform.system().lower().startswith('win'):
            os.system("pip install pynacl")
        else:
            os.system("pip3 install pynacl")
    except Exception as e:
        print("Error:", e)
        exit()


def update_encouragements(encouring_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        encouragements.append(encouring_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouring_message]


def delete_encouragements(index):
    encouragements = db["encouragements"]
    if len(encouragements) > index:
        del encouragements[index]
        db["encouragements"] = encouragements


if "responding" not in db.keys():
    db["responding"] = True


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


sad_words = []
starter_encouragments = []


def readSadFile():
    f = open("negative-words.txt", "r")
    #temp = [line.rstrip() for line in f.readlines()]
    for x in f:
        line = x.rstrip('\n')
        sad_words.append(line)


def readMotivFile():
    f = open("motiv.txt", "r")
    for x in f:
        starter_encouragments.append(x.rstrip('\n'))


client = discord.Client()
voiceFirstRun = 0


@client.event
async def on_ready():
    print('yo we have loged in biach {0.user}'.format(client))
    readMotivFile()
    readSadFile()

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.content.startswith('$hello'):
            await message.channel.send('hello')

        if message.content.startswith("$inspire"):
            quote = get_quote()
            await message.channel.send(quote)

        msg = message.content
        if db["responding"]:
            option = starter_encouragments
            if "encouragements" in db.keys():
                option = option + list(db["encouragements"])
            if any(word in msg for word in sad_words):
                await message.channel.send(random.choice(option))

        if msg.startswith("$new "):
            enouraging_message = msg.split("$new", 1)[1]
            update_encouragements(enouraging_message)
            await message.channel.send("New encouraging message was added.")

        if (msg.startswith("$del")):
            encouragments = []
            if "encouragements" in db.keys():
                index = int(msg.split("$del", 1)[1])
                delete_encouragements(index)
                encouragments = db["encouragements"]
            await message.channel.send(list(encouragments))

        if (msg.startswith("$list")):
            encouragments = []
            if "encouragements" in db.keys():
                encouragments = db["encouragements"]
            await message.channel.send(list(encouragments))

        if msg.startswith("$responding"):
            value = msg.split("$responding ", 1)[1]
            if value.lower() == "true":
                db["responding"] = True
                await message.channel.send("responding is on.")
            else:
                db["responding"] = False
                await message.channel.send("responding is off.")

        if msg.startswith("$ploi"):
            url = msg.split("$ploi ", 1)[1]
            song_there = os.path.isfile("song.mp3")
            try:
                if song_there:
                    os.remove("song.mp3")
            except PermissionError:
                await message.channel.send(
                    "wait for current to end or use stop command")
                return
            voiceChannel = discord.utils.get(
                message.channel.guild.voice_channels, name='General')
            voicClient = discord.VoiceClient(client, message.channel)
            if not voicClient.is_connected():
                try:
                    print('connecting again')
                    await voiceChannel.connect()
                except:
                    print('dont do shit')

            # voicClient = discord.VoiceClient(client, message.channel)
            voice = discord.utils.get(client.voice_clients,
                                      guild=message.channel.guild)
            # if not voicClient.is_connected():

            ydl_ops = {
                'format':
                'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with youtube_dl.YoutubeDL(ydl_ops) as ydl:
                ydl.download([url])
             
            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    os.rename(file, 'song.mp3')
            voice.play(discord.FFmpegPCMAudio("song.mp3"))
        if msg.startswith("$leave"):
            for x in client.voice_clients:
                #  print('in the fuckwe me')
                await x.disconnect()
        if msg.startswith("$resume"):
            voice = discord.utils.get(client.voice_clients,
                                      guild=message.channel.guild)
            if voice.is_paused():
                voice.resume()
            else:
                await message.send("the audio aint paused")
        if msg.startswith("$pause"):
            voice = discord.utils.get(client.voice_clients,
                                      guild=message.channel.guild)
            if voice.is_playing():
                voice.pause()
            else:
                await message.channel.send('currently no audio is playin')
        if msg.startswith("$stop"):
            voice = discord.utils.get(client.voice_clients,
                                      guild=message.channel.guild)
            if voice.is_playing():
                voice.stop()
        if msg.startswith("$Q"):
            value = msg.split("$Q ", 1)[1]
            print(value)
            wikianser = wikipedia.summary(value, sentences=10)
            print(wikianser)
            searchResult = wikipedia.search(value, results=10)
            embedVar = discord.Embed(
                title="Available wiki pages",
                description="Please replay with the $[number of the page]",
                color=0x00ff00)
            for i in range(10):
                embedVar.add_field(name=str(i + 1) + ":" + searchResult[i],
                                   value="------",
                                   inline=False)

            await message.channel.send(embed=embedVar)

            def check(m):
                return int(m.content) > 0 and int(
                    m.content) <= 10 and m.channel == message.channel

            msg = await client.wait_for('message', check=check)
            # print(msg.content)
            # if msg != '':
            print(searchResult[int(msg.content) - 1].title())
            wiki = wikipedia.summary(searchResult[int(msg.content) - 1],
                                     auto_suggest=False,
                                     sentences=10)
            await message.channel.send(wiki)
        #  print(requestedWiki)


keep_alive()
my_secret = os.environ['TOKEN']
client.run(my_secret)
