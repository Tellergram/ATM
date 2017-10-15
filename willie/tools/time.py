# coding=utf8
"""Tools for getting and displaying the time."""
from __future__ import unicode_literals
from __future__ import absolute_import

import datetime
import time
try:
    import pytz
except:
    pytz = False


def get_timezone(db=None, config=None, zone=None, nick=None, channel=None):
    """Find, and return, the approriate timezone

    Time zone is pulled in the following priority:
    1. `zone`, if it is valid
    2. The timezone for the channel or nick `zone` in `db` if one is set and
    valid.
    3. The timezone for the nick `nick` in `db`, if one is set and valid.
    4. The timezone for the channel  `channel` in `db`, if one is set and valid.
    5. The default timezone in `config`, if one is set and valid.

    If `db` is not given, or given but not set up, steps 2 and 3 will be
    skipped. If `config` is not given, step 4 will be skipped. If no step
    yeilds a valid timezone, `None` is returned.

    Valid timezones are those present in the IANA Time Zone Database. Prior to
    checking timezones, two translations are made to make the zone names more
    human-friendly. First, the string is split on `', '`, the pieces reversed,
    and then joined with `'/'`. Next, remaining spaces are replaced with `'_'`.
    Finally, strings longer than 4 characters are made title-case, and those 4
    characters and shorter are made upper-case. This means "new york, america"
    becomes "America/New_York", and "utc" becomes "UTC".

    This function relies on `pytz` being available. If it is not available,
    `None` will always be returned.
    """
    if not pytz:
        return None
    tz = None

    def check(zone):
        """Returns the transformed zone, if valid, else None"""
        if zone:
            zone = '/'.join(reversed(zone.split(', '))).replace(' ', '_')
            if len(zone) <= 4:
                zone = zone.upper()
            else:
                zone = zone.title()
            if zone in pytz.all_timezones:
                return zone
        return None

    if zone:
        tz = check(zone)
        if not tz:
            tz = check(db.get_nick_or_channel_value(zone, 'timezone'))
    if not tz and nick:
        tz = check(db.get_nick_value(nick, 'timezone'))
    if not tz and channel:
        tz = check(db.get_channel_value(channel, 'timezone'))
    if not tz and config and config.has_option('core', 'default_timezone'):
        tz = check(config.core.default_timezone)
    return tz


def format_time(db=None, config=None, zone=None, nick=None, channel=None,
                time=None):
    """Return a formatted string of the given time in the given zone.

    `time`, if given, should be a naive `datetime.datetime` object and will be
    treated as being in the UTC timezone. If it is not given, the current time
    will be used. If `zone` is given and `pytz` is available, `zone` must be
    present in the IANA Time Zone Database; `get_timezone` can be helpful for
    this. If `zone` is not given or `pytz` is not available, UTC will be
    assumed.

    The format for the string is chosen in the following order:

    1. The format for the nick `nick` in `db`, if one is set and valid.
    2. The format for the channel `channel` in `db`, if one is set and valid.
    3. The default format in `config`, if one is set and valid.
    4. ISO-8601

    If `db` is not given or is not set up, steps 1 and 2 are skipped. If config
    is not given, step 3 will be skipped."""
    tformat = None
    if db:
        if nick:
            tformat = db.get_nick_value(nick, 'time_format')
        if not tformat and channel:
            tformat = db.get_channel_value(channel, 'time_format')
    if not tformat and config and config.has_option('core',
                                                    'default_time_format'):
        tformat = config.core.default_time_format
    if not tformat:
        tformat = '%F - %T%Z'

    if not time:
        time = datetime.datetime.utcnow()

    if not pytz or not zone:
        return time.strftime(tformat)
    else:
        if not time.tzinfo:
            utc = pytz.timezone('UTC')
            time = utc.localize(time)
        zone = pytz.timezone(zone)
        return time.astimezone(zone).strftime(tformat)

def pretty_date(base_time=False):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""
	diff = time.time() - base_time
	second_diff = diff
	day_diff = int(diff / 86400)

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return "%i seconds ago" % (second_diff)
		if second_diff < 120:
			return "a minute ago"
		if second_diff < 3600:
			return "%i minutes ago" % (second_diff / 60)
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return "%i hours ago" % (second_diff / 3600)
	if day_diff == 1:
		return "yesterday (%i hours ago)" % (second_diff / 3600)
	if day_diff < 7:
		return "%i days ago" % (day_diff)
	if day_diff < 14:
		return "last week (%i days ago)" % (day_diff)
	if day_diff < 31:
		return "%i weeks ago" % (day_diff / 7)
	if day_diff < 62:
		return "last month (%i weeks ago)" % (day_diff  / 7)
	if day_diff < 365:
		return "%i months ago" % (day_diff / 30)
	if day_diff < 730:
		return "last year (%i months ago)" % (day_diff / 30)
	return "%i years ago" % (day_diff / 365)