# python

import urllib.request


def get_html_string(url):
    fp = urllib.request.urlopen(url)
    byte_html = fp.read()
    html = byte_html.decode("utf8")
    fp.close()
    return html


def get_html_page_title(yturl):
    html = get_html_string(yturl)
    keyphrase = "<title>"
    terminator_char = "<"
    foundTitle = False
    title = ""
    for i in range(len(html)):
        if foundTitle:
            break
        if html[i:(i + len(keyphrase))] == keyphrase:
            index = i + len(keyphrase)
            while html[index] != "<":
                title += html[index]
                index += 1
            foundTitle = True
    return title

def remove_end_spaces(string):
    if string[-1] != " ":
        return string
    else:
        return remove_end_spaces(string[:-1])

def filter_for_playlist(url_end):
    new_url_end = ""
    for char in url_end:
        if char == "&":
            break
        else:
            new_url_end += char
    return new_url_end



def spaces_to_pluses(string):
    string = remove_end_spaces(string)
    new_string = ""
    for c in string:
        if c == " ":
            new_string += "+"
        else:
            new_string += c
    return new_string

def main(search_query):
    baseURL = "https://www.youtube.com/results?search_query="
    html_keyphrase = "<a href=\"/watch?v="

    #search_query = "the only difference between martyrdom and suicide"
    sq = spaces_to_pluses(search_query)
    sURL = baseURL + sq

    html = get_html_string(sURL)

    url_end = ""
    foundURL = False
    for i in range(len(html)):
        if foundURL:
            break
        section = html[i:(i + len(html_keyphrase))]
        if section == html_keyphrase:
            #print("found")
            #print(html[i:i+20])
            index = i + len(html_keyphrase)
            while html[index] != "\"":
                #print("index: " + str(index) + ", char: " + str(html[index]))
                url_end += html[index]
                index += 1
            foundURL = True

    #print(url_end)
    url_end = filter_for_playlist(url_end)
    return url_end





if __name__ == '__main__':
    main(input("search_query: "))
