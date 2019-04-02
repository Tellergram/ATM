"""
remind.py - Willie Reminder Module
Copyright 2011, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.
http://willie.dftba.net
"""

import os
import re
import time
import threading
import collections
import codecs
from datetime import datetime
from willie.module import commands, example, NOLIMIT

def filename(self):
    name = self.nick + '-' + self.config.host + '.reminders.db'
    return os.path.join(self.config.dotdir, name)

def load_database(name):
    data = {}
    if os.path.isfile(name):
        f = codecs.open(name, 'r', encoding='utf-8')
        for line in f:
            unixtime, channel, nick, message = line.split('\t')
            message = message.rstrip('\n')
            t = int(float(unixtime))  # WTFs going on here?
            reminder = (channel, nick, message)
            try:
                data[t].append(reminder)
            except KeyError:
                data[t] = [reminder]
        f.close()
    return data


def dump_database(name, data):
    f = codecs.open(name, 'w', encoding='utf-8')
    for unixtime, reminders in data.iteritems():
        for channel, nick, message in reminders:
            f.write('%s\t%s\t%s\t%s\n' % (unixtime, channel, nick, message))
    f.close()


def setup(bot):
    bot.rfn = filename(bot)
    bot.rdb = load_database(bot.rfn)

    def monitor(bot):
        time.sleep(5)
        while True:
            now = int(time.time())
            unixtimes = [int(key) for key in bot.rdb]
            oldtimes = [t for t in unixtimes if t <= now]
            if oldtimes:
                for oldtime in oldtimes:
                    for (channel, nick, message) in bot.rdb[oldtime]:
                        if message:
                            bot.msg(channel, nick + ': ' + message)
                        else:
                            bot.msg(channel, nick + '!')
                    del bot.rdb[oldtime]
                dump_database(bot.rfn, bot.rdb)
            time.sleep(2.5)

    targs = (bot,)
    t = threading.Thread(target=monitor, args=targs)
    t.start()

scaling = collections.OrderedDict([
        ('years', 365.25 * 24 * 3600),
        ('year', 365.25 * 24 * 3600),
        ('yrs', 365.25 * 24 * 3600),
        ('y', 365.25 * 24 * 3600),

        ('months', 29.53059 * 24 * 3600),
        ('month', 29.53059 * 24 * 3600),
        ('mo', 29.53059 * 24 * 3600),

        ('weeks', 7 * 24 * 3600),
        ('week', 7 * 24 * 3600),
        ('wks', 7 * 24 * 3600),
        ('wk', 7 * 24 * 3600),
        ('w', 7 * 24 * 3600),

        ('days', 24 * 3600),
        ('day', 24 * 3600),
        ('d', 24 * 3600),

        ('hours', 3600),
        ('hour', 3600),
        ('hrs', 3600),
        ('hr', 3600),
        ('h', 3600),

        ('minutes', 60),
        ('minute', 60),
        ('mins', 60),
        ('min', 60),
        ('m', 60),

        ('seconds', 1),
        ('second', 1),
        ('secs', 1),
        ('sec', 1),
        ('s', 1),
        ])

periods = '|'.join(scaling.keys())


@commands('in')
@example('.in 3h45m Go to class')
def remind(bot, trigger):
    """Gives you a reminder in the given amount of time."""
    duration = 0
    message = re.split('(\d+ ?(?:' + periods + ')) ?', trigger.group(2))[1:]
    reminder = ''
    stop = False
    for piece in message:
        grp = re.match('(\d+) ?(.*) ?', piece)
        if grp and not stop:
            length = float(grp.group(1))
            factor = scaling.get(grp.group(2), 60)
            duration += length * factor
        else:
            reminder = reminder + piece
            stop = True
    if duration == 0:
        return bot.reply("Sorry, didn't understand the input.")

    if duration % 1:
        duration = int(duration) + 1
    else:
        duration = int(duration)

    create_reminder(bot, trigger, duration, reminder)


@commands('at')
@example('.at 13:47 Do your homework!')
def at(bot, trigger):
    """
    Gives you a reminder at the given time. Takes hh:mm:ssContinent/Large_City
    message. Continent/Large_City is a timezone from the tzdb; a list of valid
    options is available at http://dft.ba/-tz . The seconds and timezone are
    optional.
    """
    regex = re.compile(r'(\d+):(\d+)(?::(\d+))?([^\s\d]+)? (.*)')
    match = regex.match(trigger.group(2))
    if not match:
        bot.reply("Sorry, but I didn't understand your input.")
        return NOLIMIT
    hour, minute, second, tz, message = match.groups()
    if not second:
        second = '0'

    now = datetime.now()
    timediff = (datetime(now.year, now.month, now.day, int(hour), int(minute),
                         int(second), tzinfo=now.tzinfo)
                - now)
    duration = timediff.seconds

    if duration < 0:
        duration += 86400
        
    create_reminder(bot, trigger, duration, message)

def create_reminder(bot, trigger, duration, message):
    t = int(time.time()) + duration
    reminder = (trigger.sender, trigger.nick, message)
    try:
        bot.rdb[t].append(reminder)
    except KeyError:
        bot.rdb[t] = [reminder]

    dump_database(bot.rfn, bot.rdb)

    if duration >= 60:
        tformat = "%F - %T%Z"
        timef = datetime.fromtimestamp(t).strftime(tformat)
        bot.reply('Okay, will remind at %s' % timef)
    else:
        bot.reply('Okay, will remind in %s secs' % duration)