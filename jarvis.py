# python

import discord
import asyncio
import urllib
import csv
from texter import sendSMSMessage
import ytsearcher
import getTop100
import overpwn_news
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor



songCSVpath = "dragonsongs.csv"
addressCSVpath = "addressbook.csv"
news_channel_name = "news"

discord_username = "dragonitecatcher5556@gmail.com"
discord_password = "dratini17"
discord_token = "MjE0ODg5NzE2NzMzMDUwODgx.CpPjMw\
.ZdFLRcXEGA2ILghHvqJ5HVU7U0I"

admins = ['mike']

YTSTRING = "https://www.youtube.com/watch?v="

client = discord.Client()
voice = None
player = None
station = "hot-100"

last_update_time = 0
time_between_updates = 12 * (60 * 60)

default_volume = 8 / 100

ytr_m_channel = 'general'

hangmaning = False
hangman_word = ""
guesses = ""
tries_left = 0
hangman_guessed_chars = ""
hangman_blank_char = "="

ytring = False
current_ytr_url = ''
ytrloop = None

def wordArrayToString(words):
    string = ""
    for word in words:
        string += str(word) + " "
    string = string[:-1]
    return string

def spaces_between_letters(string):
    new_string = ""
    for i in range(len(string)):
        new_string += string[i]
        new_string += " "
    new_string = new_string[:-1]
    return new_string

def parse_yturl_end(yturl):
    if YTSTRING not in yturl:
        return yturl
    else:
        for i in range(len(yturl)):
            if yturl[i] == '=':
                return yturl[i + 1:]


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
        replyString = "I am not connected to a voice channel.\n"
        replyString += "Use $join [voice channel name]."
    return replyString

def get_hangman_word():
    '''chooses a random word from the words file'''
    wordfilename = "words.txt"
    f = open(wordfilename)
    read = csv.reader(f)
    file_data = []
    for row in read:
        file_data += row
    word = random.choice(file_data)
    return word

@asyncio.coroutine
def update_news(message):
    global news_channel_name
    global last_update_time

    for channel in message.server.channels:
        if channel.name == news_channel_name:
            news_string = overpwn_news.get_news()
            last_update_time = time.time()
            print("Updated news - update time: " + str(last_update_time))
            yield from send_discord(channel, news_string)

def split_message(message, limit):
    '''keeps the message below discords limit'''
    if len(message) < limit:
        return [message]
    else:
        message1 = message[:int(len(message) / 2)]
        message2 = message[int(len(message) / 2):]
        message1 = split_message(message1, limit)
        message2 = split_message(message2, limit)
        return message1 + message2


@asyncio.coroutine
def send_discord(channel, message):
    '''sends the message splitting it if need be'''
    character_limit = 2000
    if len(message) < character_limit:
        yield from client.send_message(channel, message)
    else:
        messages = split_message(message, character_limit)
        for message in messages:
            yield from client.send_message(channel, message)


@asyncio.coroutine
def yt_radio(m_channel):
    # threaded function
    global player
    global ytring
    global current_ytr_url

    print('starting thread')
    # init
    if ytring:
        rs = yield from playYoutubeURL(current_ytr_url)
        yield from send_discord(m_channel, rs)
    #loop
    while ytring:
        print('ytring:' + str(ytring))
        if player != None and (not player.is_playing()):
            print(player)
            current_ytr_url = ytsearcher.getUpNext(current_ytr_url)
            rs = yield from playYoutubeURL(current_ytr_url)
            yield from send_discord(m_channel, rs)
    return


@client.event
@asyncio.coroutine
def on_message(message):
    global player
    global voice
    global station
    global time_between_updates
    global last_update_time
    global hangmaning
    global hangman_word
    global guesses
    global tries_left
    global hangman_blank_char
    global hangman_guessed_chars
    global current_ytr_url
    global ytring
    global ytrloop
    global ytr_m_channel
    #check if its a command
    if False:
        print(time.time())
        print('ytring: ' + str(ytring))
        if ytrloop != None: print('ytrloop: ' + str(ytrloop.is_alive()))
        if player != None: print('player: ' + str(player.is_playing()))
        print()

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
        elif command == ('$quit') and message.author.name in admins:
            shouldReply = False
            hangmaning = False
            ytring = False
            yield from client.send_message(message.channel, 'Goodbye.')
            yield from client.logout()

        #join a voice channel
        elif command == ('$join'):
            voice = None
            if len(words) < 2:
                words += ['General']
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

        elif command == ("$leave") and message.author.name in admins:
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

        elif command == ("$ytr"):
            if ytring:
                replyString = "Stopping radioing" + "\n\n"
                ytring = False
            else:
                ytring = True
                args = words[1:]
                if len(args) < 1:
                    respString = "provide search terms"
                else:
                    arg_string = wordArrayToString(args)
                    url_end = ytsearcher.main(arg_string)
                    current_ytr_url = url_end
                    replyString = "Radioing with search terms: " + arg_string + "\n\n"
                    #ytrloop = threading.Thread(target=yt_radio, args=(message.channel,))
                    yield from asyncio.ensure_future(yt_radio(message.channel))
                    #print('bout to start thread')

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

        # updates news
        elif command == "$updatenews":
            shouldReply = False
            yield from update_news(message)


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

        # just for playing games
        elif command == ("$hangman"):
            if hangmaning:
                hangmaning = False
                replyString = "Stopping the game of hangman."
            else:
                hangmaning = True
                hangman_word = get_hangman_word()
                guesses = hangman_blank_char * len(hangman_word)
                tries_left = 7
                hangman_guessed_chars = ""
                replyString = "Starting hangman! You have " + str(tries_left) + " tries."



        # not one of the above commands
        else:
            replyString = "\"" + command + "\" is not a command."

        if shouldReply:
            yield from send_discord(message.channel, replyString)



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

    elif hangmaning:
        # playing hangman
        m = message.content
        words = m.split(" ")
        if len(words) == 1:# 1 word guess, other wise dont mess
            guess_w = words[0]
            if len(guess_w) > 1:
                if guess_w == hangman_word:
                    # win
                    hangmaning = False
                    string = "You win! The word was " + hangman_word + "."
                    yield from client.send_message(message.channel, string)
                else:
                    tries_left -= 1
                    if tries_left == 0:
                        # loss
                        hangmaning = False
                        string = "Game over! The word was " + hangman_word + "."
                        yield from client.send_message(message.channel, string)
                    else:
                        string = "Sorry, the word was not " + guess_w + "." + "\n"
                        string += "Word: " + spaces_between_letters(guesses) + "\n"
                        string += "Guessed: " + spaces_between_letters(hangman_guessed_chars) + "\n"
                        string += "You have " + str(tries_left) + " tries left."
                        yield from client.send_message(message.channel, string)
            else: # guessing a character
                if guess_w in hangman_guessed_chars:
                    string = "You have already guessed " + guess_w + "."
                    yield from client.send_message(message.channel, string)
                else:
                    hangman_guessed_chars += guess_w
                    foundchar = False
                    #
                    new_guesses = ""
                    for i in range(len(hangman_word)):
                        if guess_w == hangman_word[i]:
                            new_guesses += hangman_word[i]
                            foundchar = True
                        else:
                            new_guesses += guesses[i]
                    guesses = new_guesses
                    #
                    if foundchar:
                        if hangman_blank_char not in guesses:
                            # win
                            hangmaning = False
                            string = "You win! The word was " + hangman_word + "."
                            yield from client.send_message(message.channel, string)
                        else:
                            string = "Great work! \n"
                            string += "Word: " + spaces_between_letters(guesses) + "\n"
                            string += "Guessed: " + spaces_between_letters(hangman_guessed_chars) + "\n"
                            string += "You have " + str(tries_left) + " tries left."
                            yield from client.send_message(message.channel, string)
                    else:
                        tries_left -= 1
                        if tries_left == 0:
                            # loss
                            hangmaning = False
                            string = "Game over! The word was " + hangman_word + "."
                            yield from client.send_message(message.channel, string)
                        else:
                            string = "Sorry, " + guess_w + " was not in the word." + "\n"
                            string += "Word: " + spaces_between_letters(guesses) + "\n"
                            string += "Guessed: " + spaces_between_letters(hangman_guessed_chars) + "\n"
                            string += "You have " + str(tries_left) + " tries left."
                            yield from client.send_message(message.channel, string)


    #if (time.time() - last_update_time) > time_between_updates:
        #yield from update_news(message)



@asyncio.coroutine
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
    yield from setup()
    yield from client.login(discord_token)
    yield from client.connect()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    p = ThreadPoolExecutor(2)
    try:
        loop.run_until_complete(main())
    except:
        loop.run_until_complete(client.logout())
    finally:
        loop.close()
