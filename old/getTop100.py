# gets the songs to dj

import urllib.request
import csv
import random

#top100url = "http://www.billboard.com/charts/hot-100"
top100url = "http://www.billboard.com/charts/digital-songs"

def url_start():
    return "http://www.billboard.com/charts/"

def get_html_string(url):
    fp = urllib.request.urlopen(url)
    byte_html = fp.read()
    html = byte_html.decode("utf8")
    fp.close()
    return html

def get_phrase(html, keyphrase, terminator_char):
    foundPhrase = False
    phrase = ""
    for i in range(len(html)):
        if foundPhrase:
            break
        if html[i:(i + len(keyphrase))] == keyphrase:
            index = i + len(keyphrase)
            while html[index] != terminator_char:
                phrase += html[index]
                index += 1
            foundPhrase = True
    return phrase

def get_phrases(html, keyphrase, terminator_char):
    phrases = []
    for i in range(len(html)):
        if html[i:(i + len(keyphrase))] == keyphrase:
            index = i + len(keyphrase)
            phrase = ""
            while html[index] != terminator_char:
                phrase += html[index]
                index += 1
            phrases += [phrase]
    return phrases

def get_phrases2(html):
    phrases = []
    songphrase = "<h2 class=\"chart-row__song\">"
    artistphrase = "data-tracklabel=\"Artist Name\">"
    for i in range(len(html)):
        if html[i:(i + len(songphrase))] == songphrase:
            index = i + len(songphrase)
            song_name = ""
            while html[index] != "<":
                song_name += html[index]
                index += 1
            while html[index:(index + len(artistphrase))] != artistphrase:
                index += 1
            index += len(artistphrase)
            artist = ""
            while html[index] != "<":
                artist += html[index]
                index += 1

            phrases += [[song_name, artist]]

            #while

    #phrases += [[phrase]]
    return phrases

def replace_unusual_character(phrases, unusual, rchar):
    '''phrases to replace in
    unusual string to replace
    repleacement character'''
    for j in range(len(phrases)):
        for k in range(len(phrases[j])):
            for i in range(len(phrases[j][k])):
                if phrases[j][k][i:(i + len(unusual))] == unusual:
                    phrases[j][k] = phrases[j][k][:i] + rchar + phrases[j][k][i + len(unusual):]
    return phrases

def replace_unusual_characters(phrases):
    phrases = replace_unusual_character(phrases, "&#039;", "'")
    phrases = replace_unusual_character(phrases, "&amp;", "&")
    phrases = replace_unusual_character(phrases, "&quot;", "\"")
    return phrases

def remove_lead_lag_whitespace(phrases):
    '''removes whitespace in front of and after text'''
    whitespace = " \n\t"
    for j in range(len(phrases)):
        for k in range(len(phrases[j])):
            i = 0
            while phrases[j][k][i] in whitespace:
                i += 1
            i2 = len(phrases[j][k]) - 1
            while phrases[j][k][i2] in whitespace:
                i2 -= 1
            phrases[j][k] = phrases[j][k][i:(i2 + 1)]

    return phrases

def random_song(url):
    songs = top100(url)
    song = random.choice(songs)
    return song

def topN(n, url):
    songs = top100(url)
    if n < 0 or n >= len(songs):
        song = songs[0]
    else:
        song = songs[n]
    return song

def list_songs(url):
    songs = top100(url)
    string = ""
    count = 1
    for song in songs:
        string += str(count) + ": " + song + "\n"
        count += 1
    return string

def top100(url):
    html = get_html_string(url)

    songs = get_phrases2(html)
    songs = replace_unusual_characters(songs)
    songs = remove_lead_lag_whitespace(songs)
    new_songs = []
    for row in songs:
        new_songs += [row[0] + " " + row[1]]
    songs = new_songs
    #for line in songs:
    #    print(line)
    return songs

def main():
    song = topN(int(input("n: ")))
    print(song)


if __name__ == "__main__":
    main()
