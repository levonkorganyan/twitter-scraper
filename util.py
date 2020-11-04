from email.utils import parsedate_tz
import datetime

def read_last_line(f):
    for line in f:
        pass
    last_line = line
    return last_line;

def twitter_date_to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime.datetime(*time_tuple[:6])
    return dt - datetime.timedelta(seconds=time_tuple[-1])

def datetime_diff_days(a, b):
    return (a - b).days