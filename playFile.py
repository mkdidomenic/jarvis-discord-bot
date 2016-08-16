# python

import discord
import asyncio

client = discord.Client()
voice = None
player = None


@client.event
@asyncio.coroutine
def on_message(message):
    global player
    global voice
    if message.content.startswith("$"):
        m = message.content
        words = m.split(" ")
        replyString = ""
        if m.startswith('$greet'):
            replyString = "Hello!"
        elif m.startswith('$quit'):
            yield from client.send_message(message.channel, 'Goodbye')
            yield from client.logout()
        elif m.startswith('$join'):
            voice = None
            if len(words) < 2:
                replyString = "need to specify a channel"
            for channel in message.channel.server.channels:
                if channel.name == words[1]:
                    if channel.type == discord.ChannelType.voice:
                        voice = yield from client.join_voice_channel(channel)
                        replyString = "Joining voice channel: " + str(channel.name)
                    if channel.type == discord.ChannelType.text:
                        replyString = "Cannot join " + str(channel.name)
                        replyString += " because it is a text channel, not a voice channel"
            if replyString == "":
                replyString = "That channel does not exist"
        elif m.startswith('$play'):
            if voice != None:
                if player != None:
                    player.stop()
                player = None
                player = voice.create_ffmpeg_player('heathens.mp3')
                player.start()
                replyString = "Playing: " + voice.channel.name + " channel is bumpin'!"
                #replyString += "\nJammin' to " + words[1]
            else:
                replyString = "Not connected to a voice channel. :["
        elif m.startswith('$silence'):
            if player != None:
                player.stop()
                player = None
                replyString = "silencing!"
            else:
                replyString = "nothing is playing you dippity shit >.<"

        yield from client.send_message(message.channel, replyString)





@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print()

@asyncio.coroutine
def main():
    yield from client.login("dragonitecatcher5556@gmail.com", "dratini17")
    yield from client.connect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except:
        loop.run_until_complete(client.logout())
    finally:
        loop.close()
