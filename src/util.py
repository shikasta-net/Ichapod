
from datetime import datetime
from dateutil import parser, tz
import logging
import pytz
import re

ERROR: int = 0

__unicode_map = {
    ord(u'\xa0'):' ',
    ord(u'\u0009'):' ',
    ord(u'\u200b'):'',
    ord(u'\u2013'):'-',
    ord(u'\u2014'):'-',
    ord(u'\u2018'):'\'',
    ord(u'\u2019'):'\'',
    ord(u'\u2032'):'\'',
    ord(u'\u201c'):'\"',
    ord(u'\u201d'):'\"',
}

__ok_unicode = [
    u'\xc1',
    u'\xd3',
    u'\xe1',
    u'\xe2',
    u'\xe4',
    u'\xe9',
    u'\xeb',
    u'\xed',
    u'\xf1',
    u'\xf8',
    u'\xfc',
    u'\u0160',
    u'\u0161',
    u'\u01a1',
    u'\u0301',
    u'\u1ea1',
]

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

def set_error(code: int = 1):
    global ERROR
    if code > ERROR:
        ERROR = code

def get_error() -> int:
    return ERROR

def convert_date(date: str) -> str:
    loading_date = re.match(r'^(?P<date>\d{4}-\d{2}-\d{2}).(?P<time>\d{0,3})$', date)
    if loading_date:
        date = F"{loading_date.group('date')} {int(loading_date.group('time')):04}"
    output = "%Y-%m-%d-%H%M"
    return parser.parse(date, tzinfos=__tzinfos).strftime(output)

def tracknumber_from_date(date: str) -> str:
    epoch = parser.parse('2000-09-01') # Start of podcast history
    return str((parser.parse(date) - epoch).days)

def remove_unicode(string: str) -> str :
    clean = string.translate(__unicode_map)
    clean = squelch_whitespace(clean)

    #check that the character cleanup worked
    try :
        clean.translate({ ord(i):None for i in __ok_unicode }).encode('ascii', 'strict')
    except UnicodeEncodeError as e:
        logging.warning(F"Failed to remove character from {string}: {e}")
        return None

    return clean

def clean_title(string: str) -> str:
    clean = remove_unicode(string)
    if not clean :
        return None
    clean = re.sub(r' - ', r': ', clean)
    clean = squelch_whitespace(clean)

    return clean

def sanitise_path(string: str) -> str:
    clean = remove_unicode(string).translate(__valid_path_map)
    clean = squelch_whitespace(clean)

    return clean

def squelch_whitespace(string: str) -> str:
    return re.sub(r'\s*(?P<chr>[ ,])', r'\g<chr>', string)


class GenericBisect:
    """
    Solving the problem that bisect library doesn't support 'key', by Shnatsel - https://stackoverflow.com/questions/7380629/perform-a-binary-search-for-a-string-prefix-in-python
    """

    LOWER, HIGHER, STOP = range(3)

    def bisect(arr, comparator, lo=0, hi=None):
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(arr)
        while lo < hi:
            mid = (lo+hi)//2
            if comparator(arr, mid) == GenericBisect.STOP:
                return mid
            elif comparator(arr, mid) == GenericBisect.HIGHER:
                lo = mid+1
            else:
                hi = mid
        return lo

def string_prefix_comparator_right(prefix):
    def parametrized_string_prefix_comparator_right(array, mid):
        if array[mid][0:len(prefix)] <= prefix:
            return GenericBisect.HIGHER
        else:
            return GenericBisect.LOWER
    return parametrized_string_prefix_comparator_right

def string_prefix_comparator_left(prefix):
    def parametrized_string_prefix_comparator_left(array, mid):
        if array[mid][0:len(prefix)] < prefix: # < is the only diff. from right
            return GenericBisect.HIGHER
        else:
            return GenericBisect.LOWER
    return parametrized_string_prefix_comparator_left
