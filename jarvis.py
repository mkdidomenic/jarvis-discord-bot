# python

import discord
import asyncio
import urllib
import csv
from texter import sendSMSMessage
import ytsearcher
import getTop100


songCSVpath = "dragonsongs.csv"
addressCSVpath = "addressbook.csv"

discord_username = "dragonitecatcher5556@gmail.com"
discord_password = "dratini17"
discord_token = "MjE0ODg5NzE2NzMzMDUwODgx.CpPjMw\
.ZdFLRcXEGA2ILghHvqJ5HVU7U0I"

YTSTRING = "https://www.youtube.com/watch?v="

client = discord.Client()
voice = None
player = None
station = "hot-100"

default_volume = 15 / 100

def wordArrayToString(words):
    string = ""
    for word in words:
        string += str(word) + " "
    string = string[:-1]
    return string


def playYoutubeURL(yturl):
    global player
    global voice
    if voice != None:
        if player != None:
            player.stop()
        player = None
        # fix up the url if need be
        if YTSTRING not in yturl:
            complete_url = YTSTRING + yturl

        player = yield from voice.create_ytdl_player(complete_url)
        player.volume = default_volume
        player.start()
        replyString = "Playing - " + voice.channel.name + " channel is bumpin'!" + "\n"
        replyString += "URL: " + yturl

        # get the url page title
        displayURL = True
        if displayURL:
            ptitle = ytsearcher.get_html_page_title(complete_url)
            replyString += "\nJammin' to " + ptitle
    else:
        replyString = "I am not connected to a voice channel."
    return replyString

@client.event
@asyncio.coroutine
def on_message(message):
    global player
    global voice
    global station
    #check if its a command
    if message.content.startswith("$"):
        # get the command and message
        m = message.content
        words = m.split(" ")
        replyString = ""
        command = words[0]
        #should jarvis reply?
        shouldReply = True
        #simple response
        if command == ('$greet'):
            replyString = "Hello! I am Jarvis."

        elif command == ('$help'):
            replyString = "All commands are preceded by a $, for example, $greet\n"
            replyString += "\n-greet- gives a nice greeting"
            replyString += "\n-help - this"
            replyString += "\n-join [voice channel] - joins a voice channel to play music from"
            replyString += "\n-play [YouTube URL] - plays music from a YouTube URL"
            replyString += "\n\t-Use the part of the URL after the equals sign"
            replyString += "\n\t-https://www.youtube.com/watch?v=[this part]"
            replyString += "\n-volume [amount] - a percentage, from 0 to 200%"
            replyString += "\n-save [YouTube URL] [alias] - saves a youtube url for easy playing"
            replyString += "\n\t-[alias] must not contain spaces"
            replyString += "\n-load [alias] - loads a YouTube URL and then starts playing music"
            replyString += "\n-songs - lists the saved aliases of YouTube songs"
            replyString += "\n-text [name] [message] - texts someone in the address book the following message"
            replyString += "\n-contacts - shows the contacts address book"
            replyString += "\n-invite [server URL] - joins a server given an invite"
            replyString += "\n-leave [server name] - leaves a server given the server name"
            replyString += "\n-search [search terms] - search YouTube, playing the top result"
            replyString += "\n-dj - plays a random song from the charts station"
            replyString += "\n-dj [number] - plays the number song from the charts station"
            replyString += "\n-djlist - lists the songs on the current stations"
            replyString += "\n-djset [charts station URL]- sets the DJ station"
            replyString += "\n-stations - lists the saved stations"

        #quit the stuff
        elif command == ('$quit') and message.author.name == "mike":
            shouldReply = False
            yield from client.send_message(message.channel, 'Goodbye.')
            yield from client.logout()

        #join a voice channel
        elif command == ('$join'):
            voice = None
            if len(words) < 2:
                replyString = "You must specify a channel"
            for channel in message.channel.server.channels:
                if channel.name == words[1]:
                    if channel.type == discord.ChannelType.voice:
                        voice = yield from client.join_voice_channel(channel)
                        replyString = "Joining voice channel: " + str(channel.name)
                    if channel.type == discord.ChannelType.text:
                        replyString = "Cannot join " + str(channel.name)
                        replyString += " because it is a text channel, not a voice channel."
            if replyString == "":
                replyString = "That channel does not exist."


        #switching servers
        elif command == ('$invite'):
            if len(words) < 2:
                replyString = "You must specify a server url invite to switch to."
                replyString += "\nIt must be of the form: \"http://discord.gg/codehere\", or just the \'codehere\' part"
            else:
                target = words[1]
                inv = yield from client.get_invite(target)
                yield from client.accept_invite(inv)
                replyString = "Joining " + target

        elif command == ("$leave"):
            if len(words) < 2:
                target = message.server.name
            else:
                # for multiple worded servers
                wordlist = words[1:]
                target = ""
                for word in wordlist:
                    target += word + " "
                target = target[:-1]

            server_to_leave = None
            for server in client.servers:
                if server.name == target:
                    server_to_leave = server
            if server_to_leave != None:
                replyString = "I am leaving " + server.name + ".\n"
                yield from client.leave_server(server)
                if message.server == server_to_leave:
                    shouldReply = False
            else:
                replyString = "I am not in that server."



        # play audio
        elif command == ('$play'):

            if len(words) < 2:
                replyString = "You must specify a youtube URL."
                replyString += "\n Only including the part after the equals sign:"
                replyString += "\n" + YTSTRING
            else:
                yturl = words[1]
                replyString = yield from playYoutubeURL(yturl)

        # pause and resume the stuff
        elif command == ('$pause'):
            player.pause()
            replyString = "Paused the tunes."
        elif command == ('$resume'):
            player.resume()
            replyString = "Resumed the tunes."

        # volume adjustment
        elif command == ('$volume'):
            if len(words) < 2:
                replyString = "You must specify a volume amount"
            else:
                if player == None:
                    replyString = "I am not playing anything."
                else:
                    try:
                        percentage = float(words[1])
                        if not ((percentage >= 0) and (percentage <= 200)):
                            replyString = "The volume must be between 0 and 200."
                        else:
                            vol = percentage / 100
                            player.volume = vol
                            replyString = "I have adjusted the volume to " + str(percentage) + "%."
                    except ValueError:
                        wordstring = wordArrayToString(words[1:])
                        replyString = "\"" + wordstring + "\" is not a number between 0 and 200."

        # mute the audio
        elif command == ('$mute'):
            if player == None:
                replyString = "I am not playing anything."
            else:
                vol = 0
                player.volume = vol
                replyString = "I have adjusted the volume to " + str(vol) + "%."

        # zip it
        elif command == ('$silence'):
            if player != None:
                player.stop()
                player = None
                replyString = "Sometimes quiet is violent. |-/"
            else:
                replyString = "I am not playing anything."


        # save a youtube url as an alias
        elif command == ('$save'):
            if len(words) < 3:
                replyString = "You need to specify an alias and a URL"
            else:
                alias = wordArrayToString(words[2:])
                url = words[1]
                # get existing data
                songFile = open(songCSVpath, "r")
                read = csv.reader(songFile)
                data = []
                for row in read:
                    data += [row]

                foundAlias = False
                for row in data:
                    if row[0] == alias:
                        foundAlias = True
                if not foundAlias:
                    data += [[alias, url]]
                    songFile.close()
                    # write new data
                    songFile = open(songCSVpath, "w")
                    write = csv.writer(songFile, lineterminator='\n')
                    for row in data:
                        write.writerow(row)
                    songFile.close()
                    replyString = "I have saved url [" + url + "] as \"" + alias + "\""
                else:
                    replyString = "That alias is already in use."

        # load a youtube audio track from an presaved alias
        # triggers play with its own message
        elif command == ("$load"):
            if len(words) < 2:
                replyString = "You need to specify an alias."
            else:
                alias = wordArrayToString(words[1:])
                # get existing data
                songFile = open(songCSVpath, "r")
                read = csv.reader(songFile)
                data = []
                for row in read:
                    data += [row]
                foundAlias = False
                for row in data:
                    if row[0] == alias:
                        lalias = row[0]
                        lurl = row[1]
                        foundAlias = True
                if not foundAlias:
                    replyString = "That alias does not exist in records."
                else:
                    replyString = "\nAlias: " + lalias
                    replyString += "\nYoutube URL for playing: " + lurl + "\n\n"
                    replyString += yield from playYoutubeURL(lurl)


        # print the saved aliases
        elif command == ("$songs"):
            songFile = open(songCSVpath, "r")
            read = csv.reader(songFile)
            string = "Listing saved songs:\n\n"
            for row in read:
                string += row[0] + "\n"
            replyString = string

        # search a song on youtube, plays the top results
        elif command == ("$search"):
            args = words[1:]
            arg_string = wordArrayToString(args)
            url_end = ytsearcher.main(arg_string)
            replyString = "Search terms: " + arg_string + "\n\n"
            replyString += yield from playYoutubeURL(url_end)

        # play a song from the top 100 using search
        elif command == ("$dj"):
            sURL = getTop100.url_start() + station
            if len(words) > 1:
                songdex = int(words[1]) - 1
                st = getTop100.topN(songdex, sURL)
            else:
                st = getTop100.random_song(sURL)

            url_end = ytsearcher.main(st)

            replyString = "Station: " + station + "\n"
            replyString += "Search terms: " + st + "\n\n"
            replyString += yield from playYoutubeURL(url_end)

        #list top 100 songs
        elif command == ("$djlist"):
            sURL = getTop100.url_start() + station
            replyString = "Station: " + station + ":\n"
            replyString += getTop100.list_songs(sURL)

        #station list
        elif command == ("$stations"):
            replyString = "Current station: " + station + "\n"
            replyString += "Top 100: \"hot-100\"\n"
            replyString += "Top digital songs: \"digital-songs\"\n"
            replyString += "Top streaming songs: \"streaming-songs\"\n"
            replyString += "Top summer songs: \"summer-songs\"\n"
            replyString += "Top demanded songs: \"on-demand-songs\"\n"
            replyString += "Top twitter songs: \"twitter-top-tracks\"\n"

        # set dj station
        elif command == ("$djset"):
            if len(words) < 2:
                replyString = "You must specify a url ending."
            else:
                station = words[1]
                replyString = "Setting station to \"" + station + "\"."


        # load a file
        elif command == "$playfile":
            print("Playing file not implemented")
            if False:
                if voice != None:
                    playfilename = "file.mp4"
                    player = yield from voice.create_ffmpeg_player(playfilename)
                    player.volume = default_volume
                    player.start()
                    replyString = "Playing: " + voice.channel.name + " - file from pc."
                else:
                    replyString = "No voice channel"


        # texting
        elif command == ("$text"):
            if not (len(m) > 2):
                replyString = "You must enter a name, and a message."
            else:
                name = words[1]
                addressFile = open(addressCSVpath, "r")
                read = csv.reader(addressFile)
                data = []
                for row in read:
                    data += [row]
                foundName = False
                for row in data:
                    if row[0] == name:
                        number = row[1]
                        foundName = True
                if not foundName:
                    replyString = "That alias does not exist in records."
                else:
                    smsString = wordArrayToString(words[2:])
                    smsString += " -JARVIS"
                    sendSMSMessage("+1" + number, smsString)
                    replyString = "Texting: " + name + " (" + number + ")"

        # show the texting contacts
        elif command == ("$contacts"):
            addressFile = open(addressCSVpath, "r")
            read = csv.reader(addressFile)
            string = "Textable contacts: (Use their name)\n\n"
            for row in read:
                string += row[0] + ": " + row[1] + "\n"
            replyString = string


        # not one of the above commands
        else:
            replyString = "\"" + command + "\" is not a command."

        if shouldReply:
            character_limit = 2000
            if len(replyString) > character_limit:
                replyString1 = replyString[:character_limit]
                replyString2 = replyString[character_limit:]
                yield from client.send_message(message.channel, replyString1)
                yield from client.send_message(message.channel, replyString2)
            else:
                yield from client.send_message(message.channel, replyString)



    # responses to things people say
    elif "food" in message.content:
        # if jim is talking about food
        if message.author.name == "YoungThugJim":
            respString = "Jim's getting food? Well. It's going to be a while."
            yield from client.send_message(message.channel, respString)

    elif message.author.name == "fgt":
        # its mark
        offensive = False
        banned_words = ["fag", "gay", "idiot", "retard"]
        for word in banned_words:
            if word in message.content:
                offensive = True
        if offensive:
            #print("detected " + message.author.name + " being a jerk")
            yield from client.delete_message(message)
            respString = "That's not nice, " + message.author.name + "."
            yield from client.send_message(message.channel, respString)




def setup():
    print("setupping")
            
@client.event
@asyncio.coroutine
def on_member_join(member):
    respString = "Welcome, " + member.name + ".\n"
    if member.name == "YoungThugJim":
        respString += "\nWhat a thug."
    yield from client.send_message(member.channel, respString)


@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print()

@asyncio.coroutine
def main():
    yield from client.login(discord_token)
    yield from client.connect()
    setup()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except:
        loop.run_until_complete(client.logout())
    finally:
        loop.close()
