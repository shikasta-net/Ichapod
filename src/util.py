
from datetime import datetime
import logging
import re

__unicode_map = {
    ord(u'\xa0'):' ',
    ord(u'\u0009'):' ',
    ord(u'\u2013'):'-',
    ord(u'\u2014'):'-',
    ord(u'\u2018'):'\'',
    ord(u'\u2019'):'\'',
    ord(u'\u2032'):'\'',
    ord(u'\u201c'):'\"',
    ord(u'\u201d'):'\"',
}

__valid_path_map = {
    ord(':'):', ',
    ord('/'):', ',
    ord('?'):None,
}

def convert_date(date: str) -> datetime:
    if date[-1].isdigit() :
        input = "%a, %d %b %Y %H:%M:%S %z"
    elif date[-1].isalpha() :
        input = "%a, %d %b %Y %H:%M:%S %Z"
    output = "%Y-%m-%d-%H%M"
    return datetime.strptime(date, input).strftime(output)

def remove_unicode(string: str) -> str :
    clean = string.translate(__unicode_map)
    clean = squelch_whitespace(clean)

    #check that the character cleanup worked
    try :
        clean.encode('ascii', 'strict')
    except UnicodeEncodeError as e:
        logging.warning(F"Failed to remove character from {string}: {e}")

    return clean

def sanitise_path(string: str) -> str:
    clean = remove_unicode(string).translate(__valid_path_map)
    clean = squelch_whitespace(clean)

    return clean

def squelch_whitespace(string: str) -> str:
    return re.sub(r'\s*(?P<chr>[ ,])', r'\g<chr>', string)
