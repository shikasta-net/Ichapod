
from datetime import datetime
from dateutil import parser, tz
import logging
import pytz
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

__tzinfos = {
    'GMT': tz.gettz('Europe/GMT'),
    'PST': tz.gettz('US/Pacific'),
    'PDT': tz.gettz('US/Pacific'),
    'PT': tz.gettz('US/Pacific'),
    'MST': tz.gettz('US/Mountain'),
    'MDT': tz.gettz('US/Mountain'),
    'MT': tz.gettz('US/Mountain'),
    'CST': tz.gettz('US/Central'),
    'CDT': tz.gettz('US/Central'),
    'CT': tz.gettz('US/Central'),
    'EST': tz.gettz('US/Eastern'),
    'EDT': tz.gettz('US/Eastern'),
    'ET': tz.gettz('US/Eastern')
}

def convert_date(date: str) -> str:
    output = "%Y-%m-%d-%H%M"
    return parser.parse(date, tzinfos=__tzinfos).strftime(output)

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
