# coding=utf8
"""Functions for general usage."""
from __future__ import unicode_literals
from __future__ import absolute_import
import time

shared_var = {}
def is_integer(s):
    try:
        int(s)
    except ValueError:
        return False
    return True
    
def is_float(s):
    try:
        float(s)
    except ValueError:
        return False
    return True
    
def say(bot, msg, count=1):
    if isinstance(msg, basestring):
        msg = [msg]
    
    for m in msg:
        lines = m.splitlines()
        for l in lines:
            bot.say(l,count)
    
def mute_say(bot, trigger, msg, count=1):
    if trigger.is_privmsg:
        say(bot, msg, count)
    else:
        channel = trigger.sender.lower()
        bot.write(('MODE ', channel + ' +m'))
        say(bot, msg, count)
        bot.write(('MODE ', channel + ' -m'))

def set_delay_timer(timer, delay):
    if isinstance(timer, list):
        for t in timer:
            shared_var['delay::' + t] = time.time() + delay
    else:
        shared_var['delay::' + timer] = time.time() + delay
    
    return True
    
def get_delay_timer(timer):
    return max(0, int(round(shared_var['delay::'+timer] - time.time())))
        
def nick_online(bot, search_nick):
    search_nick = search_nick.strip()
    for channel in bot.privileges.keys():
        for nick in bot.privileges[channel]:
            if search_nick == nick or (search_nick.endswith('*') and nick.startswith(search_nick.rstrip('*'))):
                return nick
    return None
    
def inform(bot, teller, tellee, msg):
    #Check to see if user is present
    nick = nick_online(bot, tellee)
    if nick:
        bot.msg(nick,"[I] [Sent Just Now] <%s> %s" % (teller, msg))
        return nick
    else:
        timenow = time.time()
        bot.memory['tell_lock'].acquire()
        try:
            if not tellee in bot.memory['tell_dict']:
                bot.memory['tell_dict'][tellee] = [(teller, "inform", timenow, msg)]
            else:
                bot.memory['tell_dict'][tellee].append((teller, "inform", timenow, msg))
        finally:
            bot.memory['tell_lock'].release()
            return None