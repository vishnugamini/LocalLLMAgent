import pyshorteners
def shorten_url(long_url):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(long_url)
    return short_url

def shorten_urls(arr):
    fin = []
    s = pyshorteners.Shortener()
    for pic in arr:
        short_url = s.tinyurl.short(pic)
        fin.append(short_url)
    return fin
