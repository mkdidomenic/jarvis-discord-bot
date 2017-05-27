# for finding the news from overpwn

import urllib.request

overpwnURL = "http://www.overpwn.com"


def get_html_string(url):
    header = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=header)
    fp = urllib.request.urlopen(req)
    byte_html = fp.read()
    html = byte_html.decode("utf8")
    fp.close()
    return html

def get_phrase(html, keyphrase, terminator_phrase):
    foundPhrase = False
    phrase = ""
    for i in range(len(html)):
        if foundPhrase:
            break
        if html[i:(i + len(keyphrase))] == keyphrase:
            index = i + len(keyphrase)
            while html[index:(index + len(terminator_phrase))] != terminator_phrase:
                phrase += html[index]
                index += 1
            foundPhrase = True
    return phrase

def get_phrases(html, keyphrase, terminator_phrase):
    '''reverses the order of phrases for discord readability'''
    phrases = []
    for i in range(len(html)):
        if html[i:(i + len(keyphrase))] == keyphrase:
            index = i + len(keyphrase)
            phrase = ""
            while html[index:(index + len(terminator_phrase))] != terminator_phrase:
                phrase += html[index]
                index += 1
            phrases = [phrase] + phrases
    return phrases

def replace_tags(text, replace_with):
    new_text = ""
    inTags = False
    i = 0
    while i < len(text):
        if text[i] == "<":
            inTags = True
        if not inTags:
            new_text += text[i]
        if text[i] == ">":
            inTags = False
            new_text += replace_with
        i += 1
    return new_text

def replace_all(text, target, replacement):
    new_text = ""
    i = 0
    while i < len(text):
        if text[i:i + len(target)] == target:
            i += len(target)
            new_text += replacement
        else:
            new_text += text[i]
            i += 1
    return new_text

def clean_multiple_newline(text):
    nlchars = "\r\n"
    new_text = text[0:2]
    i = 2
    while i < (len(text) - 1):
        new_char = text[i]
        if text[i] in nlchars:
            if (text[i + 1] in nlchars) and (text[i - 1] in nlchars) and \
            (text[i - 2] in nlchars):
                new_char = ""
        new_text += new_char
        i += 1
    new_text += text[-1]
    return new_text

def clean_utf8(text):
    text = replace_all(text, "&nbsp;", "")
    text = replace_all(text, "&amp;", "&")
    text = replace_all(text, "&uacute;", "u")
    text = replace_all(text, "&aacute;", "a")
    text = replace_all(text, "&mdash;", " - ")
    text = replace_all(text, "&reg;", " ")
    text = replace_all(text, "&rsquo;", "\'")
    return text

def get_news():
    html = get_html_string(overpwnURL)
    key = "<section class=\"p-article-content u-typography-format\" itemprop=\"articleBody\">"

    term = "</section>"
    phrases = get_phrases(html, key, term)
    texts = ""
    for phrase in phrases:
        text = replace_tags(phrase, "")
        text = clean_utf8(text)
        text = clean_multiple_newline(text)
        texts += text + "\n" * 3
    #print(texts)
    return texts






def main():
    print("Getting overpwn news")
    get_news()

if __name__ == '__main__':
    main()
